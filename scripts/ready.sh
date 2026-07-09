#!/usr/bin/env bash
# Verifica prontidão: datasets, bundles clínicos, CKO Apgar (Fase 1).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> 1/4 Validar reference-datasets"
python3 scripts/validate_datasets.py

echo "==> 2/4 Gerar bundle de terminologia clínica"
python3 scripts/build_clinical_bundle.py

echo "==> 3/4 Sincronizar CKO Apgar v3 → UI"
python3 scripts/sync_cko_apgar_v3.py

echo "==> 4/4 Validar estrutura CKO v3 (Apgar)"
python3 scripts/validate_cko.py

echo ""
echo "Pronto. Preview local:"
echo "  cd NIFS/DELIVERY && python3 -m http.server 8765"
echo "  http://localhost:8765/preview_apgar.html"
