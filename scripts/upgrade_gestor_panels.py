#!/usr/bin/env python3
"""Substitui painel Gestor minimalista pelo mock completo (padrão Apgar)."""
from __future__ import annotations

import glob
import os
import re

HTML_DIR = os.path.join(os.path.dirname(__file__), "..", "NIFS", "DELIVERY", "html")

GESTOR_FULL = """
      <div class="tab-panel" data-tab-panel="gestor">
        <div class="gestor-notice"><svg class="icon"><use href="#i-warning"/></svg> Painel demonstrativo — dados fictícios (mock). Conecte a um backend institucional para uso em produção.</div>
        <div class="kpi-grid">
          <div class="kpi-card"><div class="kpi-label">Cálculos (7 dias)</div><div class="kpi-value">284</div><div class="kpi-sub">▲ 9% vs. semana anterior</div></div>
          <div class="kpi-card"><div class="kpi-label">Dentro da faixa esperada</div><div class="kpi-value">231</div><div class="kpi-sub">81% do total</div></div>
          <div class="kpi-card"><div class="kpi-label">Casos de alto risco</div><div class="kpi-value">37</div><div class="kpi-sub">13% do total</div></div>
          <div class="kpi-card"><div class="kpi-label">Unidades ativas</div><div class="kpi-value">4</div><div class="kpi-sub">UTI, Enfermaria, Pediatria, Emergência</div></div>
        </div>
        <div class="gestor-grid">
          <section class="calc-card">
            <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2 style="font-size:15px">Avaliações por dia (últimos 7 dias)</h2></div>
            <div class="bar-chart">
              <div class="bar-col"><span class="bar-val">38</span><div class="bar" style="height:60%"></div><span class="bar-day">Seg</span></div>
              <div class="bar-col"><span class="bar-val">33</span><div class="bar" style="height:52%"></div><span class="bar-day">Ter</span></div>
              <div class="bar-col"><span class="bar-val">41</span><div class="bar" style="height:65%"></div><span class="bar-day">Qua</span></div>
              <div class="bar-col"><span class="bar-val">36</span><div class="bar" style="height:57%"></div><span class="bar-day">Qui</span></div>
              <div class="bar-col"><span class="bar-val">44</span><div class="bar" style="height:70%"></div><span class="bar-day">Sex</span></div>
              <div class="bar-col"><span class="bar-val">29</span><div class="bar" style="height:46%"></div><span class="bar-day">Sáb</span></div>
              <div class="bar-col"><span class="bar-val">22</span><div class="bar" style="height:35%"></div><span class="bar-day">Dom</span></div>
            </div>
          </section>
          <section class="calc-card">
            <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2 style="font-size:15px">Distribuição por faixa de risco</h2></div>
            <ul class="tips-list">
              <li><svg class="icon"><use href="#i-clipcheck"/></svg> Baixo risco / dentro da faixa: 81%</li>
              <li><svg class="icon"><use href="#i-clipcheck"/></svg> Risco moderado: 6%</li>
              <li><svg class="icon"><use href="#i-clipcheck"/></svg> Alto risco / alarme: 13%</li>
            </ul>
          </section>
        </div>
        <section class="calc-card">
          <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2 style="font-size:15px">Auditoria de registro (mock)</h2></div>
          <table class="audit-table">
            <thead><tr><th>Data</th><th>Unidade</th><th>Resultado</th><th>Faixa</th><th>Registro</th></tr></thead>
            <tbody>
              <tr><td>Hoje 08:14</td><td>UTI</td><td>—</td><td>Esperada</td><td><span class="audit-ok">OK</span></td></tr>
              <tr><td>Hoje 07:52</td><td>Emergência</td><td>—</td><td>Moderada</td><td><span class="audit-ok">OK</span></td></tr>
              <tr><td>Ontem 22:10</td><td>Enfermaria</td><td>—</td><td>Esperada</td><td><span class="audit-warn">Revisar</span></td></tr>
            </tbody>
          </table>
        </section>
      </div>
"""

MINIMAL_RX = re.compile(
    r'<div class="tab-panel" data-tab-panel="gestor">.*?</div>\s*(?=\n\s*(?:</div>|<section|</main))',
    re.DOTALL,
)


def needs_upgrade(content: str) -> bool:
    if 'data-tab-panel="gestor"' not in content:
        return False
    if "gestor-grid" in content:
        return False
    return "Aguardando integração" in content or 'kpi-value">—' in content


def main() -> int:
    updated = 0
    for path in sorted(glob.glob(os.path.join(HTML_DIR, "*.html"))):
        with open(path, encoding="utf-8") as f:
            content = f.read()
        if not needs_upgrade(content):
            continue
        new_content, n = MINIMAL_RX.subn(GESTOR_FULL.strip() + "\n", content, count=1)
        if n:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            updated += 1
            print("upgraded", os.path.basename(path))
    print(f"OK: {updated} painéis Gestor atualizados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
