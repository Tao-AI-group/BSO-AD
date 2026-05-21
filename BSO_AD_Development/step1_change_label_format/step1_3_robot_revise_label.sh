# DROADO
java -jar /home/m319786/software/robot.jar template \
  --template ./step1_outputs/DROADO_labels_template.tsv \
  --prefix "ex: http://www.semanticweb.org/fangli/ontologies/2019/2/untitled-ontology-107#" \
  --output ./step1_outputs/DROADO_labels.owl \
  --errors ./step1_outputs/mini_errors.tsv \
  --force true

java -jar /home/m319786/software/robot.jar merge \
  --input ../source_ontologies/DROADO_20200628.owl \
  --input ./step1_outputs/DROADO_labels.owl \
  --output ./step1_outputs/DROADO_revise_labels.owl



# PACO
java -jar /home/m319786/software/robot.jar template \
  --template ./step1_outputs/PACO_labels_template.tsv \
  --prefix "ex: http://www.semanticweb.org/hyk038/ontologies/2018/7/untitled-ontology-17#" \
  --output ./step1_outputs/PACO_labels.owl \
  --errors ./step1_outputs/mini_errors.tsv \
  --force true

java -jar /home/m319786/software/robot.jar merge \
  --input ../source_ontologies//PACO_V02.owl \
  --input ./step1_outputs/PACO_labels.owl \
  --output ./step1_outputs/PACO_revise_labels.owl


# TEO
java -jar /home/m319786/software/robot.jar template \
  --template ./step1_outputs/TEO_labels_merged_template.tsv \
  --prefix "teo: https://sbmi.uth.edu/ontology/TEO.owl#" \
  --prefix "bfo: http://www.ifomis.org/bfo/1.1/span#" \
  --prefix "pti: https://sbmi.uth.edu/ontology/" \
  --output ./step1_outputs/TEO_labels.owl \
  --errors ./step1_outputs/mini_errors.tsv \
  --force true

java -jar /home/m319786/software/robot.jar remove \
  --input ../source_ontologies//TEO_1.0.0_20200119.owl \
  --term rdfs:label \
  --output ./step1_outputs/TEO_no_labels.owl


java -jar /home/m319786/software/robot.jar merge \
  --input ./step1_outputs/TEO_no_labels.owl \
  --input ./step1_outputs/TEO_labels.owl \
  --output ./step1_outputs/TEO_revise_labels.owl


#ADNI
java -jar /home/m319786/software/robot.jar template \
  --template ./step1_outputs/ADNI_labels_template.tsv \
  --prefix "ex: http://www.modiag.it#" \
  --output ./step1_outputs/ADNI_labels.owl \
  --errors ./step1_outputs/mini_errors.tsv \
  --force true

java -jar /home/m319786/software/robot.jar remove \
  --input ./step1_outputs/ADNI_selected_branch_clean.owl \
  --term rdfs:label \
  --output ./step1_outputs/ADNI_no_labels.owl

java -jar /home/m319786/software/robot.jar merge \
  --input ./step1_outputs/ADNI_no_labels.owl \
  --input ./step1_outputs/ADNI_labels.owl \
  --output ./step1_outputs/ADNI_revise_labels.owl
