from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "NIFS" / "reference-datasets"
DELIVERY = ROOT / "NIFS" / "DELIVERY"
DATA = DELIVERY / "js" / "modules" / "data"
BUNDLES = DELIVERY / "js" / "bundles"
MANIFEST = DELIVERY / "build-manifest.json"
ARTIFACTS = ROOT / "artifacts"
