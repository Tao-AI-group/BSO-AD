import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from owlready2 import get_ontology

model = SentenceTransformer("medicalai/ClinicalBERT")

def get_embeddings(texts):
    return model.encode(texts, normalize_embeddings=True)

def deduplicate_entities_faiss(entities, threshold=0.9):
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
    llm_data = {}
    for i, file in enumerate(llm_csv_files):
        df_ = pd.read_csv(file)
        df = df_[df_["factor_relevance"] == "Yes"]
        entities = df["entity_name"].dropna().astype(str).tolist()
        llm_data[f"llm{i+1}"] = entities
    return llm_data

def extract_ontology_concepts(ontology, top_class_label):
    top_class = None
    for cls in ontology.classes():
        label = cls.label.first() or cls.name
        if label.lower() == top_class_label.lower():
            top_class = cls
            break
    if not top_class:
        raise ValueError(f"Top-level class '{top_class_label}' not found in ontology.")
    subclasses = list(top_class.descendants())[1:]
    labels = [cls.label.first() or cls.name for cls in subclasses]
    labels = [c.replace("_", " ") for c in labels]
    return list(set(labels))

def aggregate_domain_concepts(llm_entities, dedup_threshold=0.90):
    """
    D = all BSF-relevant LLM entities aggregated across models and deduplicated.
    """
    all_entities = []
    for ents in llm_entities.values():
        all_entities.extend(ents)
    all_entities = list(set(all_entities))
    return deduplicate_entities_faiss(all_entities, threshold=dedup_threshold)

def compute_matched_domain_concepts(domain_entities, ontology_concepts, similarity_threshold=0.75):
    """
    "Domain" concepts having at least one ontology match.
    Used for: Completeness = matched_domain / total_domain
    """
    if not domain_entities or not ontology_concepts:
        return []

    domain_embs = get_embeddings(domain_entities)
    ontology_embs = get_embeddings(ontology_concepts)

    dim = ontology_embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(ontology_embs)
    scores, _ = index.search(domain_embs, 1)

    matched_domain = [
        domain_entities[i]
        for i, score in enumerate(scores[:, 0])
        if score >= similarity_threshold
    ]
    return list(set(matched_domain))

def compute_matched_ontology_concepts(domain_entities, ontology_concepts, similarity_threshold=0.75):
    """
    "Ontology" concepts having at least one domain match.
    Used for:
        Conciseness = matched_ontology / total_ontology
    """
    if not domain_entities or not ontology_concepts:
        return []

    domain_embs = get_embeddings(domain_entities)
    ontology_embs = get_embeddings(ontology_concepts)

    dim = domain_embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(domain_embs)
    scores, _ = index.search(ontology_embs, 1)

    matched_ontology = [
        ontology_concepts[i]
        for i, score in enumerate(scores[:, 0])
        if score >= similarity_threshold
    ]
    return list(set(matched_ontology))

def compute_completeness(shared_concepts, domain_entities):
    """
    Completeness = S / D
    """
    if len(domain_entities) == 0:
        return 0.0
    return len(shared_concepts) / len(domain_entities)

def compute_conciseness(shared_concepts, ontology_concepts):
    """
    Conciseness = S / O
    """
    if len(ontology_concepts) == 0:
        return 0.0
    return len(shared_concepts) / len(ontology_concepts)

def make_class_name(top_class):
    lm_lst = ["llama4", "medgemma", "qwen3"]
    prefix = "Element_Relevant_to_"
    factor_name = "_".join(top_class.split(" "))
    onto_factor_name = prefix + factor_name

    if factor_name == "Economic_stability":
        onto_factor_name = prefix + "Economic_Stability"
    if factor_name == "Social_and_Community":
        onto_factor_name = prefix + "Social_and_Community_Context"
    if factor_name == "Healthcare":
        onto_factor_name = prefix + "Health_Care"

    path = "<PATH where LLM extractions are saved>"
    lm_class_names = []
    for lm in lm_lst:
        lm_class_names.append(path + lm + "-" + factor_name + "-part2.csv")
    return onto_factor_name, lm_class_names

def main():
    base_path = <PATH to where LLM extraction and results are saved>
    owl_file = <OWL file path>
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
        "completeness": [],
        "conciseness": [],
        "num_shared_domain_concepts": [],
        "num_shared_ontology_concepts": [],
        "num_domain_concepts": [],
        "num_ontology_concepts": [],
    }

    global_data = {
        "threshold": [],
        "global_completeness": [],
        "global_conciseness": [],
        "total_shared_domain_concepts": [],
        "total_shared_ontology_concepts": [],
        "total_domain_concepts": [],
        "total_ontology_concepts": [],
    }

    for threshold in thresholds:
        all_domain_entities = []
        all_ontology_concepts = []
        onto = get_ontology(owl_file).load()

        for top_class_label in class_lst:
            factor_name, llm_csvs = make_class_name(top_class_label)
            print(f"\nProcessing class: {top_class_label} @ threshold={threshold}")

            ontology_concepts = extract_ontology_concepts(onto, factor_name)
            llm_entities = load_llm_entities(llm_csvs)

            domain_entities = aggregate_domain_concepts(llm_entities, dedup_threshold=0.90)

            matched_domain_concepts = compute_matched_domain_concepts(domain_entities, ontology_concepts, similarity_threshold=threshold)
            matched_ontology_concepts = compute_matched_ontology_concepts(domain_entities, ontology_concepts, similarity_threshold=threshold)

            completeness = compute_completeness(matched_domain_concepts, domain_entities)
            conciseness = compute_conciseness(matched_ontology_concepts, ontology_concepts)

            data["factor"].append(factor_name)
            data["threshold"].append(threshold)
            data["completeness"].append(completeness)
            data["conciseness"].append(conciseness)
            data["num_shared_ontology_concepts"].append(len(matched_ontology_concepts))
            data["num_shared_domain_concepts"].append(len(matched_domain_concepts))
            data["num_domain_concepts"].append(len(domain_entities))
            data["num_ontology_concepts"].append(len(ontology_concepts))

            all_domain_entities.extend(domain_entities)
            all_ontology_concepts.extend(ontology_concepts)

        all_domain_entities = deduplicate_entities_faiss(list(set(all_domain_entities)), threshold=0.90)
        all_ontology_concepts = list(set(all_ontology_concepts))

        all_matched_domain_concepts = compute_matched_domain_concepts(all_domain_entities, all_ontology_concepts, similarity_threshold=threshold)
        all_matched_ontology_concepts = compute_matched_ontology_concepts(all_domain_entities, all_ontology_concepts, similarity_threshold=threshold)

        global_completeness = compute_completeness(all_matched_domain_concepts,all_domain_entities)
        global_conciseness = compute_conciseness(all_matched_ontology_concepts,all_ontology_concepts)

        global_data["threshold"].append(threshold)
        global_data["global_completeness"].append(global_completeness)
        global_data["global_conciseness"].append(global_conciseness)
        global_data["total_shared_domain_concepts"].append(len(all_matched_domain_concepts))
        global_data["total_shared_ontology_concepts"].append(len(all_matched_ontology_concepts))
        global_data["total_domain_concepts"].append(len(all_domain_entities))
        global_data["total_ontology_concepts"].append(len(all_ontology_concepts))

        print(f"\n=== Global Results @ threshold={threshold} ===")
        print(f"Completeness: {global_completeness:.4f}")
        print(f"Conciseness: {global_conciseness:.4f}")
        print(f"Shared Domain Concepts: {len(all_matched_domain_concepts)}")
        print(f"Shared Domain Concepts: {len(all_matched_ontology_concepts)}")

    df = pd.DataFrame(data)
    df_global = pd.DataFrame(global_data)

    df.to_csv(base_path + "SemanticEvaluation_perClass.csv", index=False)
    df_global.to_csv(base_path + "SemanticEvaluation_Global.csv", index=False)

    print("\n=== Evaluation Completed ===")
    print(df_global)

if __name__ == "__main__":
    main()