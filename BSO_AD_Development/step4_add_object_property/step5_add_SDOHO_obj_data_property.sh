

# step1
java -jar /home/m319786/software/robot.jar export \
  --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/step4_add_dementia/step4_SDOHO_PACO_TEO_DROADO_ADNI_dementia.owl \
  --header "ID|LABEL|Type" \
  --export BSO_AD_labels_all.tsv

python step5_1_transfer_xlsx2txt.py
python step5_2_match_id_label.py



java -jar /home/m319786/software/robot.jar template \
  --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/step4_add_dementia/step4_SDOHO_PACO_TEO_DROADO_ADNI_dementia.owl \
  --template SDoH_Obpro_datapro_Literature_Ob_20250907_ID.tsv\
  --prefix "bso: https://github.com/Tao-AI-group/BSO_AD#" \
  --prefix "droado: http://www.semanticweb.org/fangli/ontologies/2019/2/untitled-ontology-107#" \
  --output step5_BSO_AD_relations.owl \



java -jar /home/m319786/software/robot.jar merge \
  --input  /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/step4_add_dementia/step4_SDOHO_PACO_TEO_DROADO_ADNI_dementia.owl \
  --input  step5_BSO_AD_relations.owl \
  --output step5_BSO_AD_relations_merged.owl