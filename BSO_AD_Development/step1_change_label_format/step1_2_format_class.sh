#DROADO
python step1_2_format_class.py ./step1_outputs/DROADO_labels_class.tsv ./step1_outputs/DROADO_labels_template.tsv

# PACO
python step1_2_format_class.py ./step1_outputs/PACO_labels_class.tsv ./step1_outputs/PACO_labels_template.tsv

#TEO
python step1_2_format_class.py ./step1_outputs/TEO_labels_class.tsv ./step1_outputs/TEO_labels_template.tsv
python step1_2_format_nonclass.py ./step1_outputs/TEO_labels_nonclass.tsv ./step1_outputs/TEO_labels_nonclass_template.tsv
python step1_2_merge_file.py


# ADNI: AD-Onto
python step1_2_format_class.py ./step1_outputs/ADNI_labels_class.tsv ./step1_outputs/ADNI_labels_template.tsv