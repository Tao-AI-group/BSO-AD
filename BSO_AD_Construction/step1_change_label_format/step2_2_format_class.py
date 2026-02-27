#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
import csv

UPPERCASE_OR_NUM_PATTERN = re.compile(r'^[A-Z0-9]+$')
lowercase_words = {"a", "an", "the", "and", "but", "or", "for", "nor", "on", "at", "to", "from", "by", "of", "in", "with"}

def to_title_case_underscores(text: str) -> str:
   
    s = text.replace(" ", "_")
    parts = [p for p in s.split("_") if p]

    
    result = []
    for i, word in enumerate(parts):
        if UPPERCASE_OR_NUM_PATTERN.match(word):
            result.append(word)
            continue
        w = word.lower()
        if i > 0 and w in lowercase_words:
            result.append(w)
        else:
            result.append(w[:1].upper() + w[1:])
    return "_".join(result)





def convert_class_name_for_adni(name: str) -> str:
    """
    Convert ontology class names into the desired format:
    - Preserve known uppercase prefixes (e.g., GDS, MMSE).
    - Insert underscores before uppercase letters, but lowercase the added parts.
    - Keep numeric suffixes intact.
    """
    # Split by existing underscores, process each part separately
    if " " in name:
        parts = name.split(" ")
        converted_words = []
        for i, w in enumerate(parts):
            if "-" in w or w.isdigit():  
                converted_words.append(w)
            elif i == 0:  
                converted_words.append(w.capitalize())
            elif w.lower() in lowercase_words:  
                converted_words.append(w.lower())
            else: 
                converted_words.append(w.capitalize())
        return "_".join(converted_words)
    
    parts = name.split("_")
    
    new_parts = []

    for part in parts:
        # Keep fully uppercase segments unchanged
        if part.isupper():
            new_parts.append(part)
            continue

        if part.isdigit():
            new_parts.append(part)
            continue

        m = re.fullmatch(r'([A-Z]{2,})Item', part)
        if m:
            acronym = m.group(1)
            new_parts.append(f"{acronym}_Item")
            continue
           

        # For mixed-case parts: Insert underscores before capital letters
        # Example: "AttentionAndCalculationItem" -> ["Attention", "And", "Calculation", "Item"]
        words = re.findall(
            r'[A-Z]{2,}(?=[A-Z][a-z]|[A-Z]|$)|[A-Z][a-z]+|[0-9]+', part
        )
        print("----")
        print(words)
        converted_words = []
        for w in words:
            if w.isupper():
                converted_words.append(w)  
            elif w.lower() in lowercase_words:
                converted_words.append(w.lower())  
            else:
                converted_words.append(w.capitalize()) 

       
        print("++++")
        print(converted_words)
        new_parts.append("_".join(converted_words))

    return "_".join(new_parts)





def get_fragment(iri: str) -> str:
    return iri.rsplit("#", 1)[-1] 




def main(in_tsv: str, out_tsv: str):
    with open(in_tsv, "r", encoding="utf-8") as fin, \
         open(out_tsv, "w", encoding="utf-8", newline="") as fout:
        reader = csv.DictReader(fin, delimiter="\t")
        writer = csv.writer(fout, delimiter="\t")

        writer.writerow(["ID", "LABEL", "Type"])
        writer.writerow(["ID", "A rdfs:label", "TYPE"])

        for row in reader:
            iri = row["ID"].strip()
            type_onto = row["Type"].strip()
            #print(type_onto)
            if type_onto.startswith("Class"):
                type_onto = "owl:Class"
         
            if row["LABEL"].strip():
                label = to_title_case_underscores(row["LABEL"].strip())
            else:
                label = to_title_case_underscores(get_fragment(iri))
            
            #for ADNI
            # if row["LABEL"].strip():
            #     label = convert_class_name_for_adni(row["LABEL"].strip())
            # else:
            #     label = convert_class_name_for_adni(get_fragment(iri)) 
            
            #### for TEO 
            print(iri.rsplit("#", 1)[:-1])
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
