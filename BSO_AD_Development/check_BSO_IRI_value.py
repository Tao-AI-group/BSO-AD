from owlready2 import get_ontology, IRIS
import re

BASE = "https://github.com/Tao-AI-group/BSO_AD#"
onto = get_ontology("step2_SDOHO_new.owl").load()

max_num = None
pat = re.compile(r"\d+")  

def consider_iri(iri):
    global max_num
    if iri.startswith(BASE):
        frag = iri.split("#", 1)[1] if "#" in iri else ""
        m = pat.findall(frag)
        if m:
            n = int("".join(m))  
            max_num = n if (max_num is None or n > max_num) else max_num

# 1) class
for c in onto.classes():
    consider_iri(c.iri)


print("Max numeric value under namespace:", max_num)