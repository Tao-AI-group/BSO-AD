#DROADO
java -jar /home/m319786/software/robot.jar export \
  --input ../source_ontologies/DROADO_20200628.owl \
  --header "ID|LABEL|Type" \
  --export ./step1_outputs/DROADO_labels_all.tsv

awk -F'\t' 'NR==1 || $3=="Class"' \
  ./step1_outputs/DROADO_labels_all.tsv > ./step1_outputs/DROADO_labels_class.tsv

#PACO
java -jar /home/m319786/software/robot.jar export \
  --input ../source_ontologies/PACO_V02.owl \
  --header "ID|LABEL|Type" \
  --export ./step1_outputs/PACO_labels_all.tsv

awk -F'\t' 'NR==1 || $3=="Class"' \
  ./step1_outputs/PACO_labels_all.tsv > ./step1_outputs/PACO_labels_class.tsv


# TEO
java -jar /home/m319786/software/robot.jar export \
  --input ../source_ontologies/TEO_1.0.0_20200119.owl \
  --header "ID|LABEL|Type" \
  --include "classes properties individuals" \
  --export ./step1_outputs/TEO_labels_all.tsv

awk -F'\t' 'NR==1 || $3=="Class"' \
  ./step1_outputs/TEO_labels_all.tsv > ./step1_outputs/TEO_labels_class.tsv

awk -F'\t' 'NR==1 || $3!="Class"' ./step1_outputs/TEO_labels_all.tsv > ./step1_outputs/TEO_labels_nonclass.tsv


# ADNI: AD-onto

# Step 1. extract branch
java -jar /home/m319786/software/robot.jar extract \
    --method TOP \
    --input ../source_ontologies/AD-Onto.owl \
    --term "http://www.modiag.it#Examination" \
    --term "http://www.modiag.it#StandardizedAssessmentItem" \
    --output ./step1_outputs/ADNI_selected_branch.owl

# Step 2. remove equivalent class
java -jar /home/m319786/software/robot.jar remove \
    --input ADNI_selected_branch.owl \
    --select self \
    --axioms equivalent \
    --output ./step1_outputs/ADNI_selected_branch_no_equiv.owl
  
java -jar /home/m319786/software/robot.jar filter \
    --input ./step1_outputs/ADNI_selected_branch_no_equiv.owl \
    --base-iri "http://www.modiag.it#" \
    --axioms internal \
    --preserve-structure false \
    --output ./step1_outputs/ADNI_selected_branch_clean.owl

java -jar /home/m319786/software/robot.jar export \
  --input ./step1_outputs/ADNI_selected_branch_clean.owl \
  --include "classes properties individuals" \
  --header "ID|LABEL|Type" \
  --export ./step1_outputs/ADNI_labels_all.tsv

awk -F'\t' 'NR==1 || $3=="Class"' \
  ./step1_outputs/ADNI_labels_all.tsv > ./step1_outputs/ADNI_labels_class.tsv
awk -F'\t' 'NR==1 || $3!="Class"' ./step1_outputs/ADNI_labels_all.tsv > ./step1_outputs/ADNI_labels_nonclass.tsv

