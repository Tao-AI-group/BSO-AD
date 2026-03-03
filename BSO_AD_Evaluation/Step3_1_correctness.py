import numpy as np
import pandas as pd
from itertools import combinations
from owlready2 import get_ontology
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load sentence embedding model
embedding_model = SentenceTransformer('medicalai/ClinicalBERT')

def get_embedding(text):
    return embedding_model.encode(text, normalize_embeddings=True)

def cosine_sim(a, b):
    return cosine_similarity([a], [b])[0][0]

# -----------------------------
#  Metric Definitions
# -----------------------------

def compute_css(child_embs):
    """
    Child Similarity Score (CSS)
    Only defined when ≥ 2 children.
    """
    if len(child_embs) < 2:
        return None  # Undefined
    sims = [cosine_sim(a, b) for a, b in combinations(child_embs, 2)]
    return float(np.mean(sims))


def compute_pss(parent_emb, child_embs):
    """
    Parent Similarity Score (PSS)
    Always defined (≥1 child).
    """
    sims = [cosine_sim(parent_emb, c) for c in child_embs]
    return float(np.mean(sims))


def compute_pda(parent_emb, child_embs):
    """
    Parent Difference Agreement (PDA)
    For 1 child → PDA = 1.0 (perfect agreement by definition)
    """
    if len(child_embs) < 2:
        return 1.0

    sims = [cosine_sim(parent_emb, c) for c in child_embs]
    std_dev = np.std(sims, ddof=1)  # sample std deviation
    pda = 1.0 - std_dev
    return float(max(0.0, min(1.0, pda)))

# -----------------------------
#  Concept Family Extraction
# -----------------------------

def extract_concept_families(ontology, root_class):
    """
    Extract (parent, [children]) for ALL parents with at least 1 child,
    matching the definition of concept families.
    """
    families = []
    for cls in root_class.descendants():
        children = list(cls.subclasses())
        if len(children) >= 1:
            families.append((cls, children))
    return families

# -----------------------------
#  Metrics per Top-Level BSF
# -----------------------------

def compute_metrics_for_root(ontology, root_class):
    print(f"\nProcessing top-level class: {root_class.name}")

    families = extract_concept_families(ontology, root_class)
    print(f"  Found {len(families)} concept families (≥1 child)")

    results = []
    skipped = 0

    for parent_cls, child_classes in families:
        try:
            parent_label = parent_cls.label.first() or parent_cls.name
            parent_label = parent_label.replace("_", " ")

            child_labels = [
                (c.label.first() or c.name).replace("_", " ")
                for c in child_classes
            ]

            parent_emb = get_embedding(parent_label)
            child_embs = [get_embedding(lbl) for lbl in child_labels]

            css = compute_css(child_embs)  # may be None
            pss = compute_pss(parent_emb, child_embs)
            pda = compute_pda(parent_emb, child_embs)

            results.append({
                'parent': parent_label,
                'children': child_labels,
                'css': css,
                'pss': pss,
                'pda': pda
            })

        except Exception as e:
            skipped += 1
            print(f"  Skipping {parent_cls.name}: {e}")
            continue

    if not results:
        print(f"  No families found under {root_class.name}")
        return None

    # Compute averages (CSS: ignore None)
    css_values = [r['css'] for r in results if r['css'] is not None]
    mean_css = np.nanmean(css_values) if len(css_values) > 0 else None
    mean_pss = float(np.mean([r['pss'] for r in results]))
    mean_pda = float(np.mean([r['pda'] for r in results]))

    print(f"  Mean CSS: {mean_css}")
    print(f"  Mean PSS: {mean_pss}")
    print(f"  Mean PDA: {mean_pda}")

    # Save per-family CSV
    df = pd.DataFrame(results)
    df.to_csv(f"{root_class.name}_Correctness_CBERT.csv", index=False)

    return {
        'root': root_class.name,
        'mean_css': mean_css,
        'mean_pss': mean_pss,
        'mean_pda': mean_pda,
        'families': len(results),
        'skipped': skipped
    }


def make_class_name(top_class):
    prefix = "Element_Relevant_to_"
    factor_name = "_".join(top_class.split(" "))
    onto_factor_name = prefix+factor_name

    if factor_name=="Economic_stability":
        onto_factor_name = prefix+"Economic_Stability"
    if factor_name=="Social_and_Community":
        onto_factor_name = prefix+"Social_and_Community_Context"
    if factor_name=="Healthcare":
        onto_factor_name = prefix+"Health_Care"
    return onto_factor_name

def main():
    owl_path = "./version2/20251002_BSO_AD.owl"
    onto = get_ontology(owl_path).load()

    class_lst = [
        "Behavior and Lifestyle",
        "Economic_stability",
        "Education_and_Literacy",
        "Food",
        "Healthcare",
        "Neighborhood",
        "Social and Community"
    ]

    all_results = []

    for name in class_lst:
        top_name = make_class_name(name)

        # Locate class
        top_class = None
        for cls in onto.classes():
            label = (cls.label.first() or cls.name)
            if label.lower() == top_name.lower():
                top_class = cls
                break

        if not top_class:
            print(f"Top-level class '{top_name}' not found.")
            continue

        summary = compute_metrics_for_root(onto, top_class)
        if summary:
            all_results.append(summary)

    df_summary = pd.DataFrame(all_results)
    df_summary.to_csv("TopLevel_Correctness_Summary_CBERT.csv", index=False)

    print("\n=== Final Summary Across BSFs ===")
    print(df_summary)


if __name__ == "__main__":
    main()