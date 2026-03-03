import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from owlready2 import get_ontology
import argparse

# Load sentence transformer model
model = SentenceTransformer("medicalai/ClinicalBERT")

def get_embeddings(texts):
    return model.encode(texts, normalize_embeddings=True)

def deduplicate_entities_faiss(entities, threshold=0.9):
    """
    Deduplicate entities using FAISS inner product (cosine sim if normalized)
    """
    if len(entities) == 0:
        return []

    embeddings = get_embeddings(entities)
    dim = embeddings.shape[1]

    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    k = min(10, len(entities))
    D, I = index.search(embeddings, k)

    visited = set()
    unique_entities = []

    for i, neighbors in enumerate(I):
        if i in visited:
            continue
        unique_entities.append(entities[i])
        for j_idx, j in enumerate(neighbors):
            if i == j:
                continue
            if D[i][j_idx] >= threshold:
                visited.add(j)

    return unique_entities

def load_llm_entities(llm_csv_files):
    """
    Load LLM entity lists from 3 CSV files.
    Returns dict: {'llm1': [...], 'llm2': [...], 'llm3': [...]}
    """
    llm_data = {}
    for i, file in enumerate(llm_csv_files):
        df_ = pd.read_csv(file)
        df = df_[df_["factor_relevance"]=="Yes"]
        entities = df["entity_name"].dropna().astype(str).tolist()
        llm_data[f"llm{i+1}"] = entities
    return llm_data

def extract_ontology_concepts(ontology, top_class_label):
    """
    Return list of leaf or subclass labels under a given top-level class.
    """
    top_class = None
    for cls in ontology.classes():
        label = cls.label.first() or cls.name
        # label = label.replace("_"," ")
        if label.lower() == top_class_label.lower():
            top_class = cls
            break
    if not top_class:
        raise ValueError(f"Top-level class '{top_class_label}' not found in ontology.")

    subclasses = list(top_class.descendants())[1:]  # exclude self
    labels = [cls.label.first() or cls.name for cls in subclasses]
    labels = [c.replace("_"," ") for c in labels]
    return list(set(labels))

def compute_shared_concepts(llm_entities, threshold=0.9):
    """
    Combine and deduplicate all LLM entities using FAISS
    """
    all_entities = []
    for ents in llm_entities.values():
        all_entities.extend(ents)
    return deduplicate_entities_faiss(all_entities, threshold)

def compute_domain_coverage(shared_entities, ontology_concepts, threshold=0.9):
    """
    Domain Coverage: % of ontology concepts matched by shared LLM entities
    """
    if not ontology_concepts or not shared_entities:
        return 0.0

    concept_embs = get_embeddings(ontology_concepts)
    shared_embs = get_embeddings(shared_entities)

    dim = concept_embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(shared_embs)

    D, _ = index.search(concept_embs, 1)
    match_count = np.sum(D >= threshold)
    return match_count / len(ontology_concepts)

def compute_ontology_relevance(llm_entities, threshold=0.9):
    """
    Relevance: average semantic overlap across all LLM pairs
    """
    names = list(llm_entities.keys())
    overlaps = []

    for i in range(len(names)):
        for j in range(i+1, len(names)):
            ents_a = deduplicate_entities_faiss(llm_entities[names[i]], threshold)
            ents_b = deduplicate_entities_faiss(llm_entities[names[j]], threshold)

            if not ents_a or not ents_b:
                overlaps.append(0.0)
                continue

            emb_a = get_embeddings(ents_a)
            emb_b = get_embeddings(ents_b)

            dim = emb_a.shape[1]
            index = faiss.IndexFlatIP(dim)
            index.add(emb_b)

            D, _ = index.search(emb_a, 1)
            match_count = np.sum(D >= threshold)
            overlap = match_count / len(ents_a)
            overlaps.append(overlap)

    return np.mean(overlaps) if overlaps else 0.0


def make_class_name(top_class):
    lm_lst = ["llama4","medgemma","qwen3"]
    prefix = "Element_Relevant_to_"

    factor_name = "_".join(top_class.split(" "))
    onto_factor_name = prefix+factor_name

    if factor_name=="Economic_stability":
        onto_factor_name = prefix+"Economic_Stability"
    if factor_name=="Social_and_Community":
        onto_factor_name = prefix+"Social_and_Community_Context"
    if factor_name=="Healthcare":
        onto_factor_name = prefix+"Health_Care"

    path = "./version2/"

    lm_class_names=[]
    for lm in lm_lst:
        lm_class_name = path+lm+"-"+factor_name+"-part2.csv"
        lm_class_names.append(lm_class_name)
    return onto_factor_name, lm_class_names

def main():
    owl_file = "./version2/BSO_AD_20250911.owl"
    thresholds = [0.75, 0.8, 0.85, 0.9, 0.95]
    class_lst = [
        "Behavior and Lifestyle",
        "Economic_stability",
        "Education_and_Literacy",
        "Food",
        "Healthcare",
        "Neighborhood",
        "Social and Community",
    ]

    data = {
        "factor": [],
        "threshold": [],
        "coverage": [],
        "relevance": [],
        "num_LLM_concepts": [],
        "num_onto_concepts": [],
    }

    # For aggregated global results
    global_data = {
        "threshold": [],
        "global_coverage": [],
        "global_relevance": [],
        "total_LLM_concepts": [],
        "total_onto_concepts": [],
    }

    for threshold in thresholds:
        all_shared_entities = []
        all_ontology_concepts = []
        all_llm_entities = {"llm1": [], "llm2": [], "llm3": []}

        onto = get_ontology(owl_file).load()

        for top_class_label in class_lst:
            factor_name, llm_csvs = make_class_name(top_class_label)
            print(f"\nProcessing class: {top_class_label} at threshold {threshold}")

            ontology_concepts = extract_ontology_concepts(onto, factor_name)
            llm_entities = load_llm_entities(llm_csvs)
            shared_entities = compute_shared_concepts(llm_entities, threshold)

            domain_coverage = compute_domain_coverage(shared_entities, ontology_concepts, threshold)
            relevance = compute_ontology_relevance(llm_entities, threshold)

            data["factor"].append(factor_name)
            data["threshold"].append(threshold)
            data["coverage"].append(domain_coverage)
            data["relevance"].append(relevance)
            data["num_LLM_concepts"].append(len(shared_entities))
            data["num_onto_concepts"].append(len(ontology_concepts))

            # accumulate for global metrics
            all_shared_entities.extend(shared_entities)
            all_ontology_concepts.extend(ontology_concepts)
            for k in all_llm_entities.keys():
                all_llm_entities[k].extend(llm_entities[k])

        # compute global aggregated metrics for this threshold
        all_shared_entities = deduplicate_entities_faiss(all_shared_entities, threshold)
        all_ontology_concepts = list(set(all_ontology_concepts))

        global_coverage = compute_domain_coverage(all_shared_entities, all_ontology_concepts, threshold)
        global_relevance = compute_ontology_relevance(all_llm_entities, threshold)

        global_data["threshold"].append(threshold)
        global_data["global_coverage"].append(global_coverage)
        global_data["global_relevance"].append(global_relevance)
        global_data["total_LLM_concepts"].append(len(all_shared_entities))
        global_data["total_onto_concepts"].append(len(all_ontology_concepts))

        print(f"\n=== Global Results (All Classes) @ threshold={threshold} ===")
        print(f"Coverage: {global_coverage:.4f}, Relevance: {global_relevance:.4f}")
        print(f"Total unique LLM concepts: {len(all_shared_entities)}")
        print(f"Total ontology concepts: {len(all_ontology_concepts)}")

    # Save per-class and global summaries
    df = pd.DataFrame(data)
    df_global = pd.DataFrame(global_data)

    base_path = "./version2/"
    df.to_csv(base_path + "Completeness_ClinicalBERT_perClass.csv", index=False)
    df_global.to_csv(base_path + "Completeness_ClinicalBERT_Global.csv", index=False)

    print("\n=== All thresholds completed ===")
    print(df_global)

if __name__ == "__main__":
    main()
