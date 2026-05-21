# DROADO
# java -jar /home/m319786/software/robot.jar template \
#   --template DROADO_labels_template.tsv \
#   --prefix "ex: http://www.semanticweb.org/fangli/ontologies/2019/2/untitled-ontology-107#" \
#   --output DROADO_labels.owl \
#   --errors mini_errors.tsv \
#   --force true

# java -jar /home/m319786/software/robot.jar merge \
#   --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/DROADO_20200628.owl \
#   --input DROADO_labels.owl \
#   --output DROADO_revise_labels.owl



# PACO
# java -jar /home/m319786/software/robot.jar template \
#   --template PACO_labels_template.tsv \
#   --prefix "ex: http://www.semanticweb.org/hyk038/ontologies/2018/7/untitled-ontology-17#" \
#   --output PACO_labels.owl \
#   --errors mini_errors.tsv \
#   --force true

# java -jar /home/m319786/software/robot.jar merge \
#   --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/PACO_V02.owl \
#   --input PACO_labels.owl \
#   --output PACO_revise_labels.owl


# TEO
java -jar /home/m319786/software/robot.jar template \
  --template TEO_labels_merged_template.tsv \
  --prefix "teo: https://sbmi.uth.edu/ontology/TEO.owl#" \
  --prefix "bfo: http://www.ifomis.org/bfo/1.1/span#" \
  --prefix "pti: https://sbmi.uth.edu/ontology/" \
  --output TEO_labels.owl \
  --errors mini_errors.tsv \
  --force true

java -jar /home/m319786/software/robot.jar remove \
  --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/TEO_1.0.0_20200119.owl \
  --term rdfs:label \
  --output TEO_no_labels.owl


java -jar /home/m319786/software/robot.jar merge \
  --input TEO_no_labels.owl \
  --input TEO_labels.owl \
  --output TEO_revise_labels.owl


#ADNI
# java -jar /home/m319786/software/robot.jar template \
#   --template ADNI_labels_template.tsv \
#   --prefix "ex: http://www.modiag.it#" \
#   --output ADNI_labels.owl \
#   --errors mini_errors.tsv \
#   --force true

# java -jar /home/m319786/software/robot.jar remove \
#   --input ADNI_selected_branch_clean.owl \
#   --term rdfs:label \
#   --output ADNI_no_labels.owl

# java -jar /home/m319786/software/robot.jar merge \
#   --input ADNI_no_labels.owl \
#   --input ADNI_labels.owl \
#   --output ADNI_revise_labels.owl
