#!/usr/bin/env bash
# Deixa o bundle DELIVERY pronto para produção.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> 1/5 Finalizar HTML (gestor, CSS crítico)"
python3 scripts/finalize_calc_delivery.py

echo "==> 2/5 Publicar HTML na raiz do site"
python3 scripts/publish_delivery.py

echo "==> 3/5 Orquestrador de segurança (pre_deploy)"
python3 -m scripts.calculator_agents orchestrate --mode pre_deploy || {
  echo "AVISO: gate de segurança falhou — ver artifacts/security/"
}

echo "==> 4/5 Validação estrutural"
python3 -m scripts.calculator_agents validate

echo "==> 5/5 Status APIs"
python3 -m scripts.calculator_agents status

echo ""
echo "Pronto. Preview local:"
echo "  cd NIFS/DELIVERY && python3 -m http.server 8765"
echo "  http://localhost:8765/imc.html"
echo ""
echo "APIs LLM: copie .env.example para .env e preencha DEEPSEEK_API_KEY"
