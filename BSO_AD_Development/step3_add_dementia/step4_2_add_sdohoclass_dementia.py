#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新增子类（自动编号 IRI）+ 用“点语法”写入 ICD10/ICD9 注释：
  entity.ICD10CM.append("Z99.0")
  entity.ICD9CM.append("799.9")

保证：
- 若本体中没有 ICD9CM 注释属性：自动创建，并绑定为 onto.ICD9CM
- 若本体中已有 ICD10CM（你提供其 IRI）：将其绑定为 onto.ICD10CM（不论原 Python 名为何）
- 解析 children 的显式前缀（推荐）与旧格式均可

TSV（Tab 分列）格式（无表头）：
parentIRI    new_label    [child1|child2~ICD10:...;ICD9:...|...]    [ICD10_for_new]    [ICD9_for_new]

示例 children 项：
  显式前缀（推荐）：
    child~ICD10:Z00.0
    child~ICD9:799.9
    child~ICD10:Z00.0,Z00.1;ICD9:799.9,799.8
  旧格式（兼容）：
    child~Z00.0,799.9   # ICD10,ICD9
    child~Z00.0         # 只有 ICD10
    child~,799.9        # 只有 ICD9
    child                # 都没有

运行示例：
python owlready_add_subclasses_icd_dot.py \
  --input A.owl \
  --output A_updated.owl \
  --id-template "https://github.com/Tao-AI-group/BSO_AD#00000" \
  --map-file add_class.txt \
  --icd10-ap-iri "https://github.com/Tao-AI-group/BSO_AD#ICD10CM" \
  --icd9-ap-iri  "https://github.com/Tao-AI-group/BSO_AD#ICD9CM"
"""

import argparse, pathlib, re, types
from typing import Optional, Iterable, Tuple
from owlready2 import get_ontology, default_world, Thing, AnnotationProperty

# ---------- ID 模板 / 生成 ----------

def parse_id_template(tmpl: str) -> Tuple[str, Optional[int]]:
    if tmpl.endswith("0"):
        m = re.match(r"^(.*?)(0+)$", tmpl)
        if not m:
            raise ValueError("Bad --id-template. Use e.g. https://...#00000 or https://...#")
        return m.group(1), len(m.group(2))
    return tmpl, None

def _iter_all_entity_iris():
    """使用公开 API 遍历当前 world 中的所有实体 IRI（类/属性/个体）。"""
    for onto in list(default_world.ontologies.values()):
        for c in onto.classes():
            if getattr(c, "iri", None): yield c.iri
        for p in onto.object_properties():
            if getattr(p, "iri", None): yield p.iri
        for p in onto.data_properties():
            if getattr(p, "iri", None): yield p.iri
        for p in onto.annotation_properties():
            if getattr(p, "iri", None): yield p.iri
        for i in onto.individuals():
            if getattr(i, "iri", None): yield i.iri

def infer_width(base: str) -> Optional[int]:
    pat = re.compile(re.escape(base) + r"(\d+)$")
    mx = 0
    for iri in _iter_all_entity_iris():
        m = pat.match(iri)
        if m:
            mx = max(mx, len(m.group(1)))
    return mx or None

def next_free_number(base: str, width: int) -> int:
    pat = re.compile(re.escape(base) + r"(\d+)$")
    mx = 0
    for iri in _iter_all_entity_iris():
        m = pat.match(iri)
        if m:
            try:
                mx = max(mx, int(m.group(1)))
            except ValueError:
                pass
    return mx + 1

def iri_exists(iri: str) -> bool:
    return default_world[iri] is not None

def make_new_iri(base: str, width: int, start: int) -> Tuple[str, int]:
    n = start
    while True:
        iri = f"{base}{str(n).zfill(width)}"
        n += 1
        if not iri_exists(iri):
            return iri, n

# ---------- TSV 读取 ----------

def read_map(path: pathlib.Path):
    rows = []
    with path.open("r", encoding="utf-8-sig") as f:
        for ln, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("\t")]
            if len(parts) < 2:
                raise ValueError(f"{path}:{ln}: Need <parentIRI>\\t<new_label>[\\tchildren][\\tICD10][\\tICD9]")
            parent = parts[0]
            new_label = parts[1]
            children = parts[2] if len(parts) >= 3 and parts[2] else None
            icd10_for_new = parts[3] if len(parts) >= 4 and parts[3] else None
            icd9_for_new  = parts[4] if len(parts) >= 5 and parts[4] else None
            rows.append((parent, new_label, children, icd10_for_new, icd9_for_new))
    return rows

# ---------- 绑定 / 创建注释属性，使其可通过 dot 语法访问 ----------

def bind_annotation_property_name(onto, prop_iri: str, desired_name: str) -> Optional[AnnotationProperty]:
    """
    将 IRI 对应的注释属性绑定为 onto.<desired_name> ，以便 entity.<desired_name>.append(...)
    - 若属性对象不存在：返回 None（调用方可决定是否跳过或创建）
    - 若存在：设置 onto.<desired_name> = 该属性对象，并返回之
    """
    prop = default_world[prop_iri]
    if prop is None:
        return None
    if not isinstance(prop, AnnotationProperty):
        print(f"[WARN] Entity at {prop_iri} is not an AnnotationProperty; dot syntax may fail.")
    # 绑定为指定名称，确保 entity.ICD10CM / entity.ICD9CM 可用
    setattr(onto, desired_name, prop)
    return prop

def ensure_icd9_property(onto, icd9_iri: str, desired_name: str = "ICD9CM_ID") -> AnnotationProperty:
    """
    确保存在注释属性 ICD9CM：
    - 若本体中已有该 IRI：绑定为 onto.ICD9CM
    - 若没有：新建，并绑定为 onto.ICD9CM
    """
    prop = default_world[icd9_iri]
    if prop is None:
        with onto:
            class ICD9CM_ID(AnnotationProperty): pass
        ICD9CM_ID.iri = icd9_iri
        prop = ICD9CM_ID
        if "ICD9CM_ID" not in prop.label:
            prop.label.append("ICD9CM_ID")
        # if "Links this class to ICD-9-CM diagnosis codes" not in prop.comment:
        #     prop.comment.append("Links this class to ICD-9-CM diagnosis codes")
        print(f"[INFO] Created AnnotationProperty: {icd9_iri}")
    setattr(onto, desired_name, prop)
    return prop

# ---------- 编码解析 ----------

def parse_codes(code_str: str):
    """
    返回 (icd10_list 或 None, icd9_list 或 None)
    支持显式前缀：ICD10:Z00.0,Z00.1;ICD9:799.9,799.8
    也兼容旧格式：Z00.0,799.9 / Z00.0, / ,799.9 / ""
    """
    if not code_str:
        return None, None
    icd10, icd9 = [], []
    if ("ICD10:" in code_str) or ("ICD9:" in code_str):
        for seg in [s.strip() for s in code_str.split(";") if s.strip()]:
            if seg.startswith("ICD10:"):
                icd10 += [c.strip() for c in seg[len("ICD10:"):].split(",") if c.strip()]
            elif seg.startswith("ICD9:"):
                icd9  += [c.strip() for c in seg[len("ICD9:"):].split(",") if c.strip()]
    else:
        parts = [c.strip() for c in code_str.split(",")]
        if len(parts) >= 1 and parts[0]: icd10.append(parts[0])
        if len(parts) >= 2 and parts[1]: icd9.append(parts[1])
    return (icd10 or None), (icd9 or None)

# ---------- 类与注释写入（点语法） ----------

def ensure_parent_class(onto, parent_iri: str):
    ent = default_world[parent_iri]
    if ent is None:
        with onto:
            Tmp = types.new_class("TempParentClass", (Thing,))
        Tmp.iri = parent_iri
        ent = Tmp
        print(f"[WARN] Parent class not declared; created placeholder: {parent_iri}")
    return ent

def create_class_with_iri(onto, iri: str, parent_cls, label: str):
    with onto:
        NewC = types.new_class("TempClass", (parent_cls,))
    NewC.iri = iri
    if label not in NewC.label:
        NewC.label.append(label)
    return NewC

def add_codes_dot(entity, onto, icd10_list, icd9_list):
    """
    用点语法写注释：
      entity.ICD10CM.append("...") / entity.ICD9CM.append("...")
    这里假定 onto.ICD10CM / onto.ICD9CM 已被绑定（见 main()）。
    若未绑定，对应 hasattr(entity, 'ICD10CM') 将为 False。
    """
    if icd10_list and hasattr(entity, "ICD10CM_ID"):
        for code in icd10_list:
            if code: entity.ICD10CM_ID.append(str(code))
    if icd9_list and hasattr(entity, "ICD9CM_ID"):
        for code in icd9_list:
            if code: entity.ICD9CM_ID.append(str(code))

# ---------- 主流程 ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="输入 OWL 文件")
    ap.add_argument("--output", required=True, help="输出 OWL 文件")
    ap.add_argument("--id-template", required=True, help='"...#00000" 或仅 "...#"')
    ap.add_argument("--map-file", required=True, help='TSV：parentIRI\\tnew_label[\\tchildren][\\tICD10][\\tICD9]')
    ap.add_argument("--icd10-ap-iri", required=True, help="ICD10CM 注释属性 IRI（已存在）")
    ap.add_argument("--icd9-ap-iri",  required=True, help="ICD9CM 注释属性 IRI（若不存在将创建）")
    ap.add_argument("--default-width", type=int, default=5)
    args = ap.parse_args()

    base, width = parse_id_template(args.id_template)

    onto = get_ontology(args.input).load()
    print(f"[INFO] Loaded: {args.input}")

    if width is None:
        width = infer_width(base) or args.default_width
    next_n = next_free_number(base, width)

    # 绑定/创建注释属性到 onto.<Name>，保证点语法可用
    prop10 = bind_annotation_property_name(onto, args.icd10_ap_iri, "ICD10CM_ID")
    if prop10 is None:
        print(f"[WARN] ICD10 AnnotationProperty not found at {args.icd10_ap_iri}; will skip ICD10 writes.")

    prop9  = ensure_icd9_property(onto, args.icd9_ap_iri, "ICD9CM_ID")

    rows = read_map(pathlib.Path(args.map_file))
    report = []

    for parent_iri, new_label, children_spec, icd10_for_new, icd9_for_new in rows:
        parent_cls = ensure_parent_class(onto, parent_iri)

        # 顶层新类
        new_iri, next_n = make_new_iri(base, width, next_n)
        new_cls = create_class_with_iri(onto, new_iri, parent_cls, new_label)
        icd10_list = [x.strip() for x in icd10_for_new.split(",")] if icd10_for_new else None
        icd9_list  = [x.strip() for x in icd9_for_new.split(",")]  if icd9_for_new  else None
        add_codes_dot(new_cls, onto, icd10_list, icd9_list)
        report.append((new_cls.iri, new_label, parent_iri,
                       ",".join(icd10_list) if icd10_list else "",
                       ",".join(icd9_list)  if icd9_list  else ""))

        # 子类
        if children_spec:
            for item in [x.strip() for x in children_spec.split("|") if x.strip()]:
                child_label = item
                child_icd10_list, child_icd9_list = None, None
                if "~" in item:
                    child_label, codes = item.split("~", 1)
                    child_icd10_list, child_icd9_list = parse_codes(codes)

                c_iri, next_n = make_new_iri(base, width, next_n)
                c_cls = create_class_with_iri(onto, c_iri, new_cls, child_label.strip())
                add_codes_dot(c_cls, onto, child_icd10_list, child_icd9_list)
                report.append((c_cls.iri, child_label.strip(), new_cls.iri,
                               ",".join(child_icd10_list) if child_icd10_list else "",
                               ",".join(child_icd9_list)  if child_icd9_list  else ""))

    onto.save(file=args.output, format="rdfxml")
    print(f"[INFO] Saved: {args.output}")

    print("IRI\tlabel\tparent\tICD10CM\tICD9CM")
    for iri, lab, par, i10, i9 in report:
        print(f"{iri}\t{lab}\t{par}\t{i10}\t{i9}")

if __name__ == "__main__":
    main()
