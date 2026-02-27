import re

def split_or_simple(s):
    return [p.strip(" ()") for p in re.split(r"\s+or\s+", s, flags=re.I)]

def match_id_label(inputfile1, inputfile2, outputfile):
    with open(inputfile1, 'r', encoding='utf-8') as f1, \
         open(inputfile2, 'r', encoding='utf-8') as f2, \
         open(outputfile, 'w', encoding='utf-8', newline='') as fw:

        ID_label_dict = {}
        for line in f1:
            line_fields = line.rstrip('\r\n').split('\t')
            ID = line_fields[0].split('#')[-1]
            label = line_fields[1]
            ID_label_dict[label] = ID

        for line2 in f2:
            line_fields2 = line2.rstrip('\r\n').split('\t')
            Domain = line_fields2[3]
            Range = line_fields2[4]
            Domain_list = split_or_simple(Domain)
            Range_list = split_or_simple(Range)
            Domain_id_list = []
            Range_id_list = []
            for Domain_item in Domain_list:
                if not Domain_item.strip():
                    continue
                if Domain_item in ID_label_dict:
                    Domain_item = "bso:" + ID_label_dict[Domain_item]
                Domain_id_list.append(Domain_item)
            for Range_item in Range_list:
                if not Range_item.strip():
                    continue
                if Range_item in ID_label_dict:
                    if Range_item == "Dementia":
                        Range_item = "droado:" + ID_label_dict[Range_item]
                    else:
                        Range_item = "bso:" + ID_label_dict[Range_item]
                Range_id_list.append(Range_item)
            if len(Domain_id_list) > 1:
                if len(Range_id_list) > 1:
                    fw.write('\t'.join(line_fields2[:3]) + '\t' + '(' +
                        ' or '.join(Domain_id_list) + ')' + '\t' + '(' +
                        ' or '.join(Range_id_list) + ')'+ '\t' +
                        '\t'.join(line_fields2[5:]) + '\n')
                else:
                   fw.write('\t'.join(line_fields2[:3]) + '\t' + '(' +
                        ' or '.join(Domain_id_list) + ')' + '\t' + 
                        ' or '.join(Range_id_list) + '\t' +
                        '\t'.join(line_fields2[5:]) + '\n') 
            else:
                if len(Range_id_list) > 1:
                    fw.write('\t'.join(line_fields2[:3]) + '\t' + 
                        ' or '.join(Domain_id_list) + '\t' + '(' +
                        ' or '.join(Range_id_list) + ')'+ '\t' +
                        '\t'.join(line_fields2[5:]) + '\n')
                else:
                   fw.write('\t'.join(line_fields2[:3]) + '\t' + 
                        ' or '.join(Domain_id_list)  + '\t' + 
                        ' or '.join(Range_id_list) + '\t' +
                        '\t'.join(line_fields2[5:]) + '\n')  

if __name__ == "__main__":
    inputfile1 = "/home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/step5_add_object_property/BSO_AD_labels_all.tsv"
    inputfile2 = "/home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/step5_add_object_property/SDoH_Obpro_datapro_Literature_Ob_20250907.tsv"
    outputfile = "/home/m319786/BSO_AD/SDOHO_redesign/robot_redesign/step5_add_object_property/SDoH_Obpro_datapro_Literature_Ob_20250907_ID.tsv"
    match_id_label(inputfile1, inputfile2, outputfile)

