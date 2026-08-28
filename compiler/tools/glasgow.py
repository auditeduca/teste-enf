from __future__ import annotations

from compiler.cko import sync_v3_to_v1
from compiler.io import load_json, mirror_under_delivery, write_generated_json
from compiler.paths import DATA, REF

V3 = DATA / "cko" / "CKO-GCS-001.json"
OVERLAY = DATA / "cko" / "overlays" / "CKO-GCS-ui.json"
OUT_CKO = DATA / "glasgow-cko.json"
EDGES_SRC = REF / "ontology" / "glasgow_edges.json"
EDGES_DATA = DATA / "glasgow-edges.json"


def build_glasgow() -> list[dict]:
    if not V3.is_file():
        raise FileNotFoundError(V3)
    if not OVERLAY.is_file():
        raise FileNotFoundError(OVERLAY)

    v3 = load_json(V3)
    overlay = load_json(OVERLAY)
    v1 = sync_v3_to_v1(v3, overlay)
    v1["metadata"]["slug"] = "glasgow"

    sources = [
        "NIFS/DELIVERY/js/modules/data/cko/CKO-GCS-001.json",
        "NIFS/DELIVERY/js/modules/data/cko/overlays/CKO-GCS-ui.json",
    ]
    entries = [
        write_generated_json(
            OUT_CKO,
            v1,
            sources=sources,
            artifact_key="js/modules/data/glasgow-cko.json",
        )
    ]

    if EDGES_SRC.is_file():
        edge_data = load_json(EDGES_SRC)
        entries.append(
            write_generated_json(
                EDGES_DATA,
                edge_data,
                sources=["NIFS/reference-datasets/ontology/glasgow_edges.json"],
                artifact_key="js/modules/data/glasgow-edges.json",
            )
        )

    mirror_under_delivery(OUT_CKO, ["js/modules/data/glasgow-cko.json", "html/js/modules/data/glasgow-cko.json"])
    if EDGES_DATA.is_file():
        mirror_under_delivery(
            EDGES_DATA,
            ["js/modules/data/glasgow-edges.json", "html/js/modules/data/glasgow-edges.json"],
        )

    return entries
