#!/usr/bin/env bash
# Deixa o bundle DELIVERY pronto para produção.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> 1/8 Compilar CKO e bundles (99 calculadoras)"
python3 -m compiler.build_all

echo "==> 2/8 Validar datasets e CKO"
python3 scripts/validate_datasets.py
python3 scripts/validate_all_cko.py

echo "==> 3/8 Painel Gestor completo (mock)"
python3 scripts/upgrade_gestor_panels.py

echo "==> 4/8 Finalizar HTML (gestor, CSS crítico)"
python3 scripts/finalize_calc_delivery.py

echo "==> 5/8 Publicar HTML na raiz do site"
python3 scripts/publish_delivery.py
python3 scripts/sync_apgar_tool_config.py

echo "==> 6/8 Orquestrador de segurança (pre_deploy)"
python3 -m scripts.calculator_agents orchestrate --mode pre_deploy || {
  echo "AVISO: gate de segurança falhou — ver artifacts/security/"
}

echo "==> 7/8 Validação estrutural"
python3 -m scripts.calculator_agents validate

echo "==> 8/8 Status APIs"
python3 -m scripts.calculator_agents status

echo ""
echo "Pronto. Preview local:"
echo "  cd NIFS/DELIVERY && python3 -m http.server 8765"
echo "  http://localhost:8765/imc.html"
