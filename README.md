# BSO-AD: Behavioral Social Data and Knowledge Ontology for ADRD

## Overview

BSO-AD is a FAIR-compliant ontology resource developed for representing and harmonizing behavioral and social factors (BSFs) and Alzheimer’s disease and related dementias (ADRD)-related knowledge. The ontology aims to support semantic interoperability, data harmonization, and knowledge integration for BSF-related ADRD research.

BSO-AD was developed following established ontology design principles with reuse of existing ontologies and controlled terminologies, including the Social Determinants of Health Ontology (SDoHO), Drug Repurposing-Oriented Alzheimer’s Disease Ontology (DROADO), AD-Onto, ICD-9-CM, and ICD-10-CM. In addition, the ontology incorporates literature-derived semantic relationships between BSFs and ADRD.

## Ontology Development

The construction of BSO-AD followed established ontology engineering principles, including OBO Foundry and FAIR principles. The ontology was developed using Protégé and ROBOT.

The ontology development framework is illustrated below.

<img src="figures/BSO-AD_Development_Framework.jpeg">


## Ontology Evaluation

Ontology quality was evaluated through Hootation-based domain expert review and a scalable LLM-assisted ontology assessment framework.

The LLM-assisted ontology evaluation framework incorporated embedding-based semantic analysis using ClinicalBERT embeddings and included ontology coverage and semantic coherence evaluation metrics, including:

- Completeness
- Conciseness
- Child Similarity Score (CSS)
- Parent-Child Similarity Score (PSS)
- Parent-Child Difference Agreement (PDA)

The evaluation workflow combined literature-derived concept extraction, ontology-guided concept aggregation, and embedding-based semantic consistency analysis.

## Citation

If you use BSO-AD or the associated LLM-assisted ontology evaluation framework in your research, please cite the following paper:

```bibtex
@article{li2026bsoad,
  title={BSO-AD: An Ontology for Representing and Harmonizing Behavioral Social Knowledge in ADRD},
  author={Li, Haifang and Yu, Yue and Bhandarkar, Avanti and Kumar, Rakesh and Clark, Isaac Heath and Hu, Yutong and Cao, Weiguo and Zhao, Na and Li, Fang and Tao, Cui},
  journal={medRxiv},
  year={2026},
  url={https://doi.org/10.64898/2026.03.30.26349756}
}
```
## License

BSO-AD is licensed under the Creative Commons Attribution 4.0 International Public License(CC BY 4.0). Please see the License File for more information.

