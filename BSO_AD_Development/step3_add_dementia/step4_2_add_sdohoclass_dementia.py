#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Automatically generate ontology subclasses with incremental IRIs
and append ICD10/ICD9 annotations using Owlready2 dot syntax.

Annotation examples:
    entity.ICD10CM.append("Z99.0")
    entity.ICD9CM.append("799.9")

Features:
- Automatically creates ICD9 annotation property if it does not exist
- Binds existing ICD10 annotation property using the provided IRI
- Supports both explicit-prefix and legacy child code formats

Input TSV format (tab-separated, without header):
parentIRI    new_label    [child1|child2~ICD10:...;ICD9:...|...]    [ICD10_for_new]    [ICD9_for_new]

Example child entries:
    Explicit-prefix format (recommended):
        child~ICD10:Z00.0
        child~ICD9:799.9
        child~ICD10:Z00.0,Z00.1;ICD9:799.9,799.8

    Legacy format (supported):
        child~Z00.0,799.9   # ICD10, ICD9
        child~Z00.0         # ICD10 only
        child~,799.9        # ICD9 only
        child               # no codes

Example usage:
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

# ---------- IRI template and ID generation ----------

def parse_id_template(tmpl: str) -> Tuple[str, Optional[int]]:
    """
    Parse the IRI template.

    Example:
        https://...#00000

    Returns:
        base IRI and numeric width
    """
    if tmpl.endswith("0"):
        m = re.match(r"^(.*?)(0+)$", tmpl)
        if not m:
            raise ValueError("Bad --id-template. Use e.g. https://...#00000 or https://...#")
        return m.group(1), len(m.group(2))
    return tmpl, None

def _iter_all_entity_iris():
    """
    Iterate through all ontology entity IRIs
    in the current Owlready2 world.
    """
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
    """
    Infer numeric ID width from existing ontology IRIs.
    """
    pat = re.compile(re.escape(base) + r"(\d+)$")
    mx = 0
    for iri in _iter_all_entity_iris():
        m = pat.match(iri)
        if m:
            mx = max(mx, len(m.group(1)))
    return mx or None

def next_free_number(base: str, width: int) -> int:
    """
    Determine the next available numeric identifier.
    """
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
    """
    Check whether an entity with the given IRI already exists.
    """
    return default_world[iri] is not None

def make_new_iri(base: str, width: int, start: int) -> Tuple[str, int]:
    """
    Generate a new unused ontology IRI.
    """
    n = start
    while True:
        iri = f"{base}{str(n).zfill(width)}"
        n += 1
        if not iri_exists(iri):
            return iri, n

# ---------- TSV parsing ----------

def read_map(path: pathlib.Path):
    """
    Read the subclass mapping TSV file.
    """
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

# ---------- Bind or create annotation properties for dot-style access ----------

def bind_annotation_property_name(onto, prop_iri: str, desired_name: str) -> Optional[AnnotationProperty]:
    """
    Bind an annotation property IRI to onto.<desired_name>
    so that dot-style syntax can be used:

        entity.<desired_name>.append(...)

    Returns:
        - None if the property does not exist
        - The annotation property object if successfully bound
    """
    prop = default_world[prop_iri]
    if prop is None:
        return None
    if not isinstance(prop, AnnotationProperty):
        print(f"[WARN] Entity at {prop_iri} is not an AnnotationProperty; dot syntax may fail.")
    # Optional annotation property description
        # if "Links this class to ICD-9-CM diagnosis codes" not in prop.comment:
        #     prop.comment.append(
        #         "Links this class to ICD-9-CM diagnosis codes"
        #     )
    setattr(onto, desired_name, prop)
    return prop

def ensure_icd9_property(onto, icd9_iri: str, desired_name: str = "ICD9CM_ID") -> AnnotationProperty:
    """
    Ensure that the ICD9 annotation property exists.

    If the property already exists:
        - bind it to onto.<desired_name>

    Otherwise:
        - create the annotation property
        - bind it to onto.<desired_name>
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

# ---------- ICD code parsing ----------

def parse_codes(code_str: str):
    """
    Parse ICD10 and ICD9 codes.

    Supported explicit-prefix format:
        ICD10:Z00.0,Z00.1;ICD9:799.9,799.8

    Supported legacy format:
        Z00.0,799.9
        Z00.0,
        ,799.9
        ""

    Returns:
        (icd10_list or None, icd9_list or None)
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

# ---------- Ontology class creation and annotation writing ----------

def ensure_parent_class(onto, parent_iri: str):
    """
    Ensure that the parent ontology class exists.

    If the class does not exist, create a temporary placeholder class.
    """
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
    Add ICD10 and ICD9 annotations using Owlready2 dot syntax.

    Example:
        entity.ICD10CM.append("...")
        entity.ICD9CM.append("...")

    Assumes:
        onto.ICD10CM and onto.ICD9CM
        have already been bound in main().
    """
    if icd10_list and hasattr(entity, "ICD10CM_ID"):
        for code in icd10_list:
            if code: entity.ICD10CM_ID.append(str(code))
    if icd9_list and hasattr(entity, "ICD9CM_ID"):
        for code in icd9_list:
            if code: entity.ICD9CM_ID.append(str(code))

# ---------- Main workflow ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Input OWL file")
    ap.add_argument("--output", required=True, help="Output OWL file")
    ap.add_argument("--id-template", required=True, help='IRI template, e.g. "...#00000" or "...#"')
    ap.add_argument("--map-file", required=True, help="TSV mapping file: "
            "parentIRI\\tnew_label"
            "[\\tchildren][\\tICD10][\\tICD9]")
    ap.add_argument("--icd10-ap-iri", required=True, help="IRI of existing ICD10 annotation property")
    ap.add_argument("--icd9-ap-iri",  required=True, help="IRI of ICD9 annotation property, (created automatically if missing)")
    ap.add_argument("--default-width", type=int, default=5)
    args = ap.parse_args()

    base, width = parse_id_template(args.id_template)

    onto = get_ontology(args.input).load()
    print(f"[INFO] Loaded: {args.input}")

    if width is None:
        width = infer_width(base) or args.default_width
    next_n = next_free_number(base, width)

   
    prop10 = bind_annotation_property_name(onto, args.icd10_ap_iri, "ICD10CM_ID")
    if prop10 is None:
        print(f"[WARN] ICD10 AnnotationProperty not found at {args.icd10_ap_iri}; will skip ICD10 writes.")

    prop9  = ensure_icd9_property(onto, args.icd9_ap_iri, "ICD9CM_ID")

    rows = read_map(pathlib.Path(args.map_file))
    report = []

    for parent_iri, new_label, children_spec, icd10_for_new, icd9_for_new in rows:
        parent_cls = ensure_parent_class(onto, parent_iri)

        # top new class
        new_iri, next_n = make_new_iri(base, width, next_n)
        new_cls = create_class_with_iri(onto, new_iri, parent_cls, new_label)
        icd10_list = [x.strip() for x in icd10_for_new.split(",")] if icd10_for_new else None
        icd9_list  = [x.strip() for x in icd9_for_new.split(",")]  if icd9_for_new  else None
        add_codes_dot(new_cls, onto, icd10_list, icd9_list)
        report.append((new_cls.iri, new_label, parent_iri,
                       ",".join(icd10_list) if icd10_list else "",
                       ",".join(icd9_list)  if icd9_list  else ""))

        #sub class
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
