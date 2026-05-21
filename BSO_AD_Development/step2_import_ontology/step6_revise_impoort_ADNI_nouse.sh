# Step 1. extract branch
java -jar /home/m319786/software/robot.jar extract \
    --method TOP \
    --input modiag_adni_ontology__v06_FT.owl \
    --term "http://www.modiag.it#Examination" \
    --term "http://www.modiag.it#StandardizedAssessmentItem" \
    --output ADNI_selected_branch.owl

# # Step 2. remove equivalent class
java -jar /home/m319786/software/robot.jar remove \
    --input ADNI_selected_branch.owl \
    --select self \
    --axioms equivalent \
    --output ADNI_selected_branch_no_equiv.owl
  
java -jar /home/m319786/software/robot.jar filter \
    --input ADNI_selected_branch_no_equiv.owl \
    --base-iri "http://www.modiag.it#" \
    --axioms internal \
    --preserve-structure false \
    --output ADNI_selected_branch_clean.owl

# step 3 import ADNI selected branch
java -jar /home/m319786/software/robot.jar merge \
  --input step5_SDOHO_PACO_TEO_DROADO.owl \
  --input ADNI_selected_branch_clean.owl \
  --collapse-import-closure true \
  --output step6_SDOHO_PACO_TEO_DROADO_ADNI.owl