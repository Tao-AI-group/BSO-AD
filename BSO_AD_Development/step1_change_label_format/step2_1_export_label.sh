#DROADO
# java -jar /home/m319786/software/robot.jar export \
#   --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/DROADO_20200628.owl \
#   --header "ID|LABEL|Type" \
#   --export DROADO_labels_all.tsv

# awk -F'\t' 'NR==1 || $3=="Class"' \
#   DROADO_labels_all.tsv > DROADO_labels_class.tsv

#PACO
# java -jar /home/m319786/software/robot.jar export \
#   --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/PACO_V02.owl \
#   --header "ID|LABEL|Type" \
#   --export PACO_labels_all.tsv

# awk -F'\t' 'NR==1 || $3=="Class"' \
#   PACO_labels_all.tsv > PACO_labels_class.tsv


# TEO
java -jar /home/m319786/software/robot.jar export \
  --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/TEO_1.0.0_20200119.owl \
  --header "ID|LABEL|Type" \
  --include "classes properties individuals" \
  --export TEO_labels_all.tsv

awk -F'\t' 'NR==1 || $3=="Class"' \
  TEO_labels_all.tsv > TEO_labels_class.tsv

awk -F'\t' 'NR==1 || $3!="Class"' TEO_labels_all.tsv > TEO_labels_nonclass.tsv


# ADNI

# # Step 1. extract branch
# java -jar /home/m319786/software/robot.jar extract \
#     --method TOP \
#     --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/modiag_adni_ontology__v06_FT.owl \
#     --term "http://www.modiag.it#Examination" \
#     --term "http://www.modiag.it#StandardizedAssessmentItem" \
#     --output ADNI_selected_branch.owl

# # Step 2. remove equivalent class
# java -jar /home/m319786/software/robot.jar remove \
#     --input ADNI_selected_branch.owl \
#     --select self \
#     --axioms equivalent \
#     --output ADNI_selected_branch_no_equiv.owl
  
# java -jar /home/m319786/software/robot.jar filter \
#     --input ADNI_selected_branch_no_equiv.owl \
#     --base-iri "http://www.modiag.it#" \
#     --axioms internal \
#     --preserve-structure false \
#     --output ADNI_selected_branch_clean.owl

# java -jar /home/m319786/software/robot.jar export \
#   --input ADNI_selected_branch_clean.owl \
#   --include "classes properties individuals" \
#   --header "ID|LABEL|Type" \
#   --export ADNI_labels_all.tsv

# awk -F'\t' 'NR==1 || $3=="Class"' \
#   ADNI_labels_all.tsv > ADNI_labels_class.tsv
# awk -F'\t' 'NR==1 || $3!="Class"' ADNI_labels_all.tsv > ADNI_labels_nonclass.tsv

