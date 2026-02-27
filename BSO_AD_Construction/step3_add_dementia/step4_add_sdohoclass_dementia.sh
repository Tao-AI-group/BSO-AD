python step4_1_transfer_xlsx2txt.py


python step4_2_add_sdohoclass_dementia.py \
  --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/step3_import_ontology/step3_SDOHO_PACO_TEO_DROADO_ADNI.owl \
  --output step4_SDOHO_PACO_TEO_DROADO_ADNI_dementia.owl \
  --id-template "https://github.com/Tao-AI-group/BSO_AD#00000" \
  --map-file add_class.txt \
  --icd10-ap-iri "https://github.com/Tao-AI-group/BSO_AD#ICD10CM" \
  --icd9-ap-iri  "https://github.com/Tao-AI-group/BSO_AD#ICD9CM"