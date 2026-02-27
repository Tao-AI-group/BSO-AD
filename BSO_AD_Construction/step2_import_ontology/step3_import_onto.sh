# PACO
java -jar /home/m319786/software/robot.jar merge \
  --input /home/m319786/BSO_AD/SDOHO_redesign/step2_SDOHO_new.owl \
  --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/step2_change_label_format/PACO_revise_labels.owl \
  --collapse-import-closure true \
  --output step3_SDOHO_PACO.owl

# TEO
java -jar /home/m319786/software/robot.jar merge \
  --input step3_SDOHO_PACO.owl \
  --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/step2_change_label_format/TEO_revise_labels.owl \
  --collapse-import-closure true \
  --output step3_SDOHO_PACO_TEO.owl

# DROADO

java -jar /home/m319786/software/robot.jar merge \
  --input step3_SDOHO_PACO_TEO.owl \
  --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/step2_change_label_format/DROADO_revise_labels.owl \
  --collapse-import-closure true \
  --output step3_SDOHO_PACO_TEO_DROADO.owl

# ADNI

java -jar /home/m319786/software/robot.jar merge \
  --input step3_SDOHO_PACO_TEO_DROADO.owl \
  --input /home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/step2_change_label_format/ADNI_revise_labels.owl \
  --collapse-import-closure true \
  --output step3_SDOHO_PACO_TEO_DROADO_ADNI.owl