from __future__ import annotations

from compiler.cko import apply_calc_definition, find_calc_definition, sync_v3_to_v1
from compiler.io import load_json, mirror_under_delivery, write_generated_json
from compiler.paths import DATA, REF

V3 = DATA / "cko" / "CKO-APGAR-001.json"
OVERLAY = DATA / "cko" / "overlays" / "CKO-APGAR-ui.json"
OUT_CKO = DATA / "apgar-cko.json"
EDGES_SRC = REF / "ontology" / "apgar_edges.json"
EDGES_DATA = DATA / "apgar-edges.json"
EDGES_BUNDLE = DATA.parents[1] / "bundles" / "edges-apgar.json"
CALC_DEF = REF / "clinical" / "calculator_definitions.json"


def build_apgar() -> list[dict]:
    """Compila artefatos Apgar; retorna entradas de manifesto."""
    if not V3.is_file():
        raise FileNotFoundError(V3)
    if not OVERLAY.is_file():
        raise FileNotFoundError(OVERLAY)

    v3 = load_json(V3)
    overlay = load_json(OVERLAY)
    v1 = sync_v3_to_v1(v3, overlay)

    if CALC_DEF.is_file():
        definition = find_calc_definition(load_json(CALC_DEF), "CALC.TOOL.APGAR")
        if definition:
            v1 = apply_calc_definition(v1, definition)

    sources = [
        "NIFS/DELIVERY/js/modules/data/cko/CKO-APGAR-001.json",
        "NIFS/DELIVERY/js/modules/data/cko/overlays/CKO-APGAR-ui.json",
        "NIFS/reference-datasets/clinical/calculator_definitions.json",
    ]
    entries = [
        write_generated_json(
            OUT_CKO,
            v1,
            sources=sources,
            artifact_key="js/modules/data/apgar-cko.json",
        )
    ]

    if EDGES_SRC.is_file():
        edge_sources = ["NIFS/reference-datasets/ontology/apgar_edges.json"]
        edge_data = load_json(EDGES_SRC)
        for dst in (EDGES_DATA, EDGES_BUNDLE):
            entries.append(
                write_generated_json(
                    dst,
                    edge_data,
                    sources=edge_sources,
                    artifact_key=str(dst.relative_to(dst.parents[3])).replace("\\", "/"),
                )
            )

    mirror_under_delivery(
        OUT_CKO,
        [
            "js/modules/data/apgar-cko.json",
            "html/js/modules/data/apgar-cko.json",
        ],
    )
    if EDGES_DATA.is_file():
        mirror_under_delivery(
            EDGES_DATA,
            [
                "js/modules/data/apgar-edges.json",
                "html/js/modules/data/apgar-edges.json",
            ],
        )

    return entries
