#DROADO
#python step2_2_format_class.py DROADO_labels_class.tsv DROADO_labels_template.tsv

# PACO
# python step2_2_format_class.py PACO_labels_class.tsv PACO_labels_template.tsv

#TEO
python step2_2_format_class.py TEO_labels_class.tsv TEO_labels_template.tsv
python step2_2_format_nonclass.py TEO_labels_nonclass.tsv TEO_labels_nonclass_template.tsv
python step2_2_merge_file.py


# ADNI
# python step2_2_format_class.py ADNI_labels_class.tsv ADNI_labels_template.tsv