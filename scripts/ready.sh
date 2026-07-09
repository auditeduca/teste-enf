#!/usr/bin/env bash
# Gate Fase 1–2: datasets, compiler, CKO, artefatos gerados.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> 1/6 Validar reference-datasets"
python3 scripts/validate_datasets.py

echo "==> 2/6 Compiler — regenerar artefatos DELIVERY"
python3 -m compiler.build_all

echo "==> 3/6 Verificar artefatos gerados (_generated + manifest)"
python3 -m compiler.verify

echo "==> 4/6 Validar CKO v3 (Apgar + Glasgow)"
python3 scripts/validate_cko.py

echo "==> 5/6 Testes CIR (Apgar + Glasgow)"
node scripts/test_cir_inference.mjs

echo "==> 6/6 Diff guard (artefatos vs git, se em CI)"
if [ "${CI:-}" = "true" ] && [ -n "$(git status --porcelain NIFS/DELIVERY/js/bundles NIFS/DELIVERY/js/modules/data/apgar-cko.json NIFS/DELIVERY/js/modules/data/apgar-edges.json NIFS/DELIVERY/js/modules/data/glasgow-cko.json NIFS/DELIVERY/js/modules/data/glasgow-edges.json NIFS/DELIVERY/build-manifest.json 2>/dev/null)" ]; then
  echo "ERRO: artefatos gerados divergem do commit — rode: python3 -m compiler.build_all && git add" >&2
  git status --porcelain NIFS/DELIVERY/js/bundles NIFS/DELIVERY/js/modules/data/apgar-cko.json NIFS/DELIVERY/js/modules/data/apgar-edges.json NIFS/DELIVERY/js/modules/data/glasgow-cko.json NIFS/DELIVERY/js/modules/data/glasgow-edges.json NIFS/DELIVERY/build-manifest.json || true
  exit 1
fi

echo ""
echo "Pronto. Preview local:"
echo "  cd NIFS/DELIVERY && python3 -m http.server 8765"
echo "  http://localhost:8765/preview_apgar.html"
echo "  http://localhost:8765/preview_glasgow.html"
