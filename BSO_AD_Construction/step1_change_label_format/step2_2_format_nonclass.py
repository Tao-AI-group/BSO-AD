import re
import sys
import csv


def main(in_tsv: str, out_tsv: str):
    with open(in_tsv, "r", encoding="utf-8") as fin, \
         open(out_tsv, "w", encoding="utf-8", newline="") as fout:
        reader = csv.DictReader(fin, delimiter="\t")
        writer = csv.writer(fout, delimiter="\t")

        # writer.writerow(["ID", "LABEL"])
        # writer.writerow(["ID", "A rdfs:label"])

        for row in reader:
            iri = row["ID"].strip()
            label = row["LABEL"].strip()
            type_onto = row["Type"].strip()
            print(type_onto)
            
            if type_onto.startswith("Data"):
                type_onto = "owl:DataProperty"
            elif type_onto.startswith("Object"):
                type_onto = "owl:ObjectProperty" 
            elif type_onto.startswith("Annotation"):
                type_onto = "owl:AnnotationProperty"
            #### for TEO 
            #print(iri.rsplit("#", 1)[:-1])
            if iri.startswith("https://sbmi.uth.edu/ontology/TEO.owl#"):
               writer.writerow(["teo:"+iri.rsplit("#", 1)[-1] , label, type_onto])
            elif iri.startswith("http://www.ifomis.org/bfo/1.1/span#"):
               writer.writerow(["bfo:"+iri.rsplit("#", 1)[-1] , label, type_onto]) 
            else:
               writer.writerow(["pti:"+iri.rsplit("/")[-1] , label, type_onto])  


    
            #writer.writerow(["ex:"+iri.rsplit("#", 1)[-1] , label])

    print(f" Done! Wrote {out_tsv}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python format_labels_tsv.py DROADO_labels.tsv labels_template.tsv")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
