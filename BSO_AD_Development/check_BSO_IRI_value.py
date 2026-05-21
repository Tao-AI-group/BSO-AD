from owlready2 import get_ontology, IRIS
import re

BASE = "https://github.com/Tao-AI-group/BSO_AD#"
onto = get_ontology("step2_SDOHO_new.owl").load()

max_num = None
pat = re.compile(r"\d+")  # 提取连续数字

def consider_iri(iri):
    global max_num
    if iri.startswith(BASE):
        frag = iri.split("#", 1)[1] if "#" in iri else ""
        m = pat.findall(frag)
        if m:
            n = int("".join(m))  # 把所有数字拼起来，如 BSO_AD_000123 -> 123
            max_num = n if (max_num is None or n > max_num) else max_num

# 1) 类
for c in onto.classes():
    consider_iri(c.iri)

# # 2) 各类属性
# for p in list(onto.properties()):
#     consider_iri(p.iri)
# for p in list(onto.object_properties()):
#     consider_iri(p.iri)
# for p in list(onto.data_properties()):
#     consider_iri(p.iri)
# for p in list(onto.annotation_properties()):
#     consider_iri(p.iri)

# # 3) 个体
# for i in onto.individuals():
#     consider_iri(i.iri)

print("Max numeric value under namespace:", max_num)
