/* ==========================================================================
   js/cognitive-ui.js — Nurse-PaLM Cognitive UI
   ==========================================================================
   Renderiza o pensamento clínico do Nurse-PaLM como extensão natural
   da calculadora — mesmos tokens, mesmos ícones Font Awesome, mesmo
   ritmo visual. Não é um dashboard separado, é o raciocínio do enfermeiro.
   ========================================================================== */
(function (global) {
  "use strict";

  const NP = global.NursePaLM;
  if (!NP) { console.error("cognitive-ui requires nurse-palm.js"); return; }

  // ═══════════════════════════════════════════════════════════════
  // STATE LABELS (PT-BR)
  // ═══════════════════════════════════════════════════════════════
  const STATE_LABELS = {
    volemia: "Volemia",
    contractilidade: "Contractilidade",
    resistenciaVascular: "Resistência Vascular",
    oxigenacao: "Oxigenação",
    ventilacao: "Ventilação",
    funcaoRenal: "Função Renal",
    inflamacao: "Inflamação",
    eletrolitos: "Eletrólitos"
  };

  // Cores semânticas (alinhadas ao design system)
  const RANK_COLORS = {
    critical: "#ef4444",
    high: "#f59e0b",
    moderate: "#2563eb",
    low: "#2563eb",
    normal: "#5b6b7f",
    unknown: "#94a3b8"
  };
  const RANK_LABELS = {
    critical: "Crítico",
    high: "Alto",
    moderate: "Moderado",
    low: "Baixo",
    normal: "Normal",
    unknown: "—"
  };

  // Ícones Font Awesome por seção
  const ICONS = {
    attention:  'fa-solid fa-eye',
    belief:     'fa-solid fa-brain',
    diagnosis:  'fa-solid fa-stethoscope',
    council:    'fa-solid fa-users',
    simulation: 'fa-solid fa-chart-line',
    trace:      'fa-solid fa-list-check',
    plan:       'fa-solid fa-clipboard-list',
    evidence:   'fa-solid fa-flask'
  };

  // ═══════════════════════════════════════════════════════════════
  // ATTENTION HEATMAP (Layer 5)
  // ═══════════════════════════════════════════════════════════════
  function renderAttentionHeatmap(container, attentionResult) {
    if (!container || !attentionResult) return;
    const signals = attentionResult.ranked || [];

    let html = '<div class="cog-section">' +
      '<h4 class="cog-section-title"><i class="' + ICONS.attention + '"></i> Atenção Clínica</h4>' +
      '<div class="cog-attention-grid">';

    for (const s of signals) {
      const color = RANK_COLORS[s.rank] || RANK_COLORS.unknown;
      const pct = Math.round(s.attentionScore * 100);
      html += '<div class="cog-attention-card" style="border-left-color:' + color + ';">' +
        '<div class="cog-attention-header">' +
          '<span class="cog-attention-type">' + (STATE_LABELS[s.type] || s.type) + '</span>' +
          '<span class="cog-attention-rank" style="color:' + color + ';">' + (RANK_LABELS[s.rank] || s.rank) + '</span>' +
        '</div>' +
        '<div class="cog-attention-value">' + s.value + ' ' + (s.unit || '') + '</div>' +
        '<div class="cog-attention-bar">' +
          '<div class="cog-attention-bar-fill" style="width:' + pct + '%; background:' + color + ';"></div>' +
        '</div>' +
        '<div class="cog-attention-score">Score: ' + pct + '% · Z=' + (s.zScore || 0).toFixed(1) + '</div>' +
      '</div>';
    }

    if (signals.length === 0) {
      html += '<p class="cog-empty">Nenhum sinal crítico detectado.</p>';
    }

    html += '</div></div>';
    container.innerHTML += html;
  }

  // ═══════════════════════════════════════════════════════════════
  // BELIEF STATE (Layer 4 + 6)
  // ═══════════════════════════════════════════════════════════════
  function renderBeliefState(container, belief, variance) {
    if (!container) return;
    const vars = NP.STATE_VARS || [];
    let html = '<div class="cog-section">' +
      '<h4 class="cog-section-title"><i class="' + ICONS.belief + '"></i> Estado Fisiológico</h4>' +
      '<div class="cog-belief-grid">';

    for (const v of vars) {
      const value = belief[v] || 0.5;
      const unc = variance ? Math.sqrt(variance[v] || 0) : 0;
      const pct = Math.round(value * 100);
      const uncPct = Math.round(unc * 100);
      const status = value < 0.3 ? "low" : value > 0.7 ? "high" : "normal";
      const statusColor = status === "low" ? "#ef4444" : status === "high" ? "#f59e0b" : "#2563eb";

      html += '<div class="cog-belief-card">' +
        '<div class="cog-belief-label">' + (STATE_LABELS[v] || v) + '</div>' +
        '<div class="cog-belief-bar-container">' +
          '<div class="cog-belief-bar" style="width:' + pct + '%; background:' + statusColor + ';"></div>' +
          '<div class="cog-belief-uncertainty" style="left:' + Math.max(0, pct - uncPct/2) + '%; width:' + uncPct + '%;"></div>' +
        '</div>' +
        '<div class="cog-belief-values">' +
          '<span>' + pct + '%</span>' +
          '<span class="cog-belief-unc">±' + uncPct + '%</span>' +
        '</div>' +
      '</div>';
    }

    html += '</div></div>';
    container.innerHTML += html;
  }

  // ═══════════════════════════════════════════════════════════════
  // NANDA DIAGNOSIS CARDS (Layer 1)
  // ═══════════════════════════════════════════════════════════════
  function renderDiagnoses(container, diagnoses) {
    if (!container) return;
    let html = '<div class="cog-section">' +
      '<h4 class="cog-section-title"><i class="' + ICONS.diagnosis + '"></i> Diagnóstico NANDA-I</h4>';

    if (!diagnoses || diagnoses.length === 0) {
      html += '<p class="cog-empty">Nenhuma hipótese diagnóstica acima do threshold.</p></div>';
      container.innerHTML += html;
      return;
    }

    html += '<div class="cog-dx-list">';
    for (let i = 0; i < diagnoses.length; i++) {
      const dx = diagnoses[i];
      const prob = Math.round(dx.probability * 100);
      const isPrimary = i === 0;
      html += '<div class="cog-dx-card' + (isPrimary ? ' cog-dx-primary' : '') + '">' +
        '<div class="cog-dx-header">' +
          '<span class="cog-dx-code">' + dx.code + '</span>' +
          (isPrimary ? '<span class="cog-dx-badge">PRIMÁRIO</span>' : '') +
        '</div>' +
        '<div class="cog-dx-name">' + dx.name + '</div>' +
        '<div class="cog-dx-prob-bar">' +
          '<div class="cog-dx-prob-fill" style="width:' + prob + '%;"></div>' +
        '</div>' +
        '<div class="cog-dx-prob-label">P = ' + prob + '%</div>';

      if (dx.evidence && dx.evidence.length > 0) {
        html += '<div class="cog-dx-evidence">';
        for (const ev of dx.evidence) {
          html += '<span class="cog-dx-evidence-tag">' + ev + '</span>';
        }
        html += '</div>';
      }

      html += '</div>';
    }
    html += '</div></div>';
    container.innerHTML += html;
  }

  // ═══════════════════════════════════════════════════════════════
  // COUNCIL DELIBERATION (Layer 10)
  // ═══════════════════════════════════════════════════════════════
  function renderCouncil(container, councilResult) {
    if (!container || !councilResult) return;
    const positions = councilResult.positions || [];
    const consensus = councilResult.consensus || "unknown";

    const consensusLabel = {
      reached: '<i class="fa-solid fa-check"></i> Consenso Alcançado',
      partial: '<i class="fa-solid fa-bolt"></i> Consenso Parcial',
      no_consensus: '<i class="fa-solid fa-xmark"></i> Sem Consenso',
      vetoed: '<i class="fa-solid fa-ban"></i> Vetoado'
    };

    let html = '<div class="cog-section">' +
      '<h4 class="cog-section-title"><i class="' + ICONS.council + '"></i> Conselho Multiagente</h4>' +
      '<div class="cog-consensus-badge cog-consensus-' + consensus + '">' + (consensusLabel[consensus] || consensus) + '</div>' +
      '<div class="cog-council-grid">';

    for (const pos of positions) {
      const confPct = Math.round(pos.confidence * 100);
      html += '<div class="cog-agent-card" style="border-top-color:' + (pos.color || '#2563eb') + ';">' +
        '<div class="cog-agent-header">' +
          '<span class="cog-agent-name">' + pos.name + '</span>';
      if (pos.veto) html += '<span class="cog-agent-veto">VETO</span>';
      html += '</div>' +
        '<div class="cog-agent-argument">' + pos.argument + '</div>' +
        '<div class="cog-agent-confidence">' +
          '<div class="cog-agent-conf-bar"><div style="width:' + confPct + '%;"></div></div>' +
          '<span>Confiança: ' + confPct + '%</span>' +
        '</div>' +
      '</div>';
    }

    html += '</div></div>';
    container.innerHTML += html;
  }

  // ═══════════════════════════════════════════════════════════════
  // SIMULATION TRAJECTORY (Layer 9)
  // ═══════════════════════════════════════════════════════════════
  function renderSimulation(container, simulation) {
    if (!container || !simulation) return;
    const trajectory = simulation.trajectory || [];
    const outcome = simulation.expectedOutcome || "unknown";

    const outcomeLabel = {
      improved: '<i class="fa-solid fa-arrow-trend-up"></i> Melhora esperada',
      stable: '<i class="fa-solid fa-minus"></i> Estável',
      unchanged: '<i class="fa-solid fa-circle-exclamation"></i> Sem mudança',
      deteriorated: '<i class="fa-solid fa-arrow-trend-down"></i> Deterioração'
    };

    let html = '<div class="cog-section">' +
      '<h4 class="cog-section-title"><i class="' + ICONS.simulation + '"></i> Simulação Clínica</h4>' +
      '<div class="cog-sim-outcome cog-sim-' + outcome + '">' + (outcomeLabel[outcome] || outcome) + '</div>' +
      '<div class="cog-sim-trajectory">';

    for (let i = 0; i < trajectory.length; i++) {
      const state = trajectory[i];
      html += '<div class="cog-sim-step">' +
        '<div class="cog-sim-step-label">T' + i + '</div>';
      for (const v of NP.STATE_VARS.slice(0, 4)) {
        const val = Math.round((state[v] || 0.5) * 100);
        html += '<div class="cog-sim-bar" title="' + (STATE_LABELS[v] || v) + ': ' + val + '%">' +
          '<div style="height:' + val + '%;"></div>' +
        '</div>';
      }
      html += '</div>';
    }

    html += '</div></div>';
    container.innerHTML += html;
  }

  // ═══════════════════════════════════════════════════════════════
  // COGNITIVE TRACE TIMELINE (all layers)
  // ═══════════════════════════════════════════════════════════════
  function renderTrace(container, trace) {
    if (!container || !trace) return;
    const steps = trace.steps || [];

    let html = '<div class="cog-section">' +
      '<h4 class="cog-section-title"><i class="' + ICONS.trace + '"></i> Rastreamento do Raciocínio</h4>' +
      '<div class="cog-trace-timeline">';

    for (const step of steps) {
      html += '<div class="cog-trace-step">' +
        '<div class="cog-trace-marker"><i class="fa-solid fa-circle" style="font-size:10px;"></i></div>' +
        '<div class="cog-trace-content">' +
          '<span class="cog-trace-layer">' + (step.layer || '') + '</span>' +
          '<span class="cog-trace-name">' + (step.name || '') + '</span>';
      if (step.detail) html += '<span class="cog-trace-detail">' + step.detail + '</span>';
      html += '</div>' +
      '</div>';
    }

    html += '</div></div>';
    container.innerHTML += html;
  }

  // ═══════════════════════════════════════════════════════════════
  // PLAN (intervenções NIC recomendadas)
  // ═══════════════════════════════════════════════════════════════
  function renderPlan(container, plan) {
    if (!container || !plan) return;
    const interventions = plan.interventions || [];
    let html = '<div class="cog-section">' +
      '<h4 class="cog-section-title"><i class="' + ICONS.plan + '"></i> Plano de Intervenções (NIC)</h4>';

    if (interventions.length === 0) {
      html += '<p class="cog-empty">Nenhuma intervenção recomendada.</p></div>';
      container.innerHTML += html;
      return;
    }

    html += '<div class="cog-dx-list">';
    for (const int of interventions) {
      html += '<div class="cog-plan-card">' +
        '<div><span class="cog-plan-code">' + (int.code || '') + '</span> <span class="cog-plan-name">' + (int.name || '') + '</span></div>' +
        '<span class="cog-plan-cost">' + (int.cost || '') + '</span>' +
      '</div>';
    }
    html += '</div></div>';
    container.innerHTML += html;
  }

  // ═══════════════════════════════════════════════════════════════
  // FULL RENDER (tabs)
  // ═══════════════════════════════════════════════════════════════
  function renderCognitivePanel(panelEl, result) {
    if (!panelEl || !result) return;

    // Remove hidden state
    panelEl.classList.remove('cip-hidden');

    const content = panelEl.querySelector('#cognitivePanelContent')
      || panelEl.querySelector('[data-cognitive-panel-content]')
      || panelEl;
    content.innerHTML = '';

    // Tabs
    const tabsHtml = '<div class="cog-tabs" role="tablist">' +
      '<button class="cog-tab active" data-cog-tab="diagnosis" role="tab"><i class="' + ICONS.diagnosis + '"></i> Diagnóstico</button>' +
      '<button class="cog-tab" data-cog-tab="attention" role="tab"><i class="' + ICONS.attention + '"></i> Atenção</button>' +
      '<button class="cog-tab" data-cog-tab="belief" role="tab"><i class="' + ICONS.belief + '"></i> Estado</button>' +
      '<button class="cog-tab" data-cog-tab="plan" role="tab"><i class="' + ICONS.plan + '"></i> Plano</button>' +
      '<button class="cog-tab" data-cog-tab="council" role="tab"><i class="' + ICONS.council + '"></i> Conselho</button>' +
      '<button class="cog-tab" data-cog-tab="simulation" role="tab"><i class="' + ICONS.simulation + '"></i> Simulação</button>' +
      '<button class="cog-tab" data-cog-tab="trace" role="tab"><i class="' + ICONS.trace + '"></i> Rastreamento</button>' +
    '</div>' +
    '<div class="cog-tab-content" data-cog-content="diagnosis"></div>' +
    '<div class="cog-tab-content hidden" data-cog-content="attention"></div>' +
    '<div class="cog-tab-content hidden" data-cog-content="belief"></div>' +
    '<div class="cog-tab-content hidden" data-cog-content="plan"></div>' +
    '<div class="cog-tab-content hidden" data-cog-content="council"></div>' +
    '<div class="cog-tab-content hidden" data-cog-content="simulation"></div>' +
    '<div class="cog-tab-content hidden" data-cog-content="trace"></div>';

    content.innerHTML = tabsHtml;

    // Render each tab
    const dxContainer = content.querySelector('[data-cog-content="diagnosis"]');
    renderDiagnoses(dxContainer, result.diagnoses);

    const attContainer = content.querySelector('[data-cog-content="attention"]');
    renderAttentionHeatmap(attContainer, result.attention);

    const beliefContainer = content.querySelector('[data-cog-content="belief"]');
    renderBeliefState(beliefContainer, result.belief, result.variance);

    const planContainer = content.querySelector('[data-cog-content="plan"]');
    renderPlan(planContainer, result.plan);

    const councilContainer = content.querySelector('[data-cog-content="council"]');
    renderCouncil(councilContainer, result.council);

    const simContainer = content.querySelector('[data-cog-content="simulation"]');
    renderSimulation(simContainer, result.simulation);

    const traceContainer = content.querySelector('[data-cog-content="trace"]');
    renderTrace(traceContainer, result.trace);

    // Tab switching
    const tabs = content.querySelectorAll('.cog-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const target = tab.dataset.cogTab;
        content.querySelectorAll('.cog-tab-content').forEach(c => {
          c.classList.toggle('hidden', c.dataset.cogContent !== target);
        });
      });
    });
  }

  // ═══════════════════════════════════════════════════════════════
  // PUBLIC API
  // ═══════════════════════════════════════════════════════════════
  async function renderCognitivePanelEntry(panelElOrId, patientContextOrResult) {
    var panel = typeof panelElOrId === "string" ? document.getElementById(panelElOrId) : panelElOrId;
    if (!panel) panel = document.getElementById("cognitivePanel");
    if (!panel) return null;

    var content = panel.querySelector("#cognitivePanelContent")
      || panel.querySelector("[data-cognitive-panel-content]")
      || panel;
    var payload = patientContextOrResult;

    if (payload && payload.observations && global.NursePaLM && global.NursePaLM.runCognitivePipeline) {
      panel.classList.remove("cip-hidden");
      content.innerHTML = '<div class="cog-loading"><i class="fa-solid fa-spinner fa-spin"></i> Analisando raciocínio clínico...</div>';
      try {
        payload = await global.NursePaLM.runCognitivePipeline(patientContextOrResult);
        content._cognitiveResult = payload;
      } catch (e) {
        content.innerHTML = '<div class="cog-error">Não foi possível executar a análise cognitiva.</div>';
        throw e;
      }
    }

    if (payload) renderCognitivePanel(panel, payload);
    return payload;
  }

  global.CognitiveUI = {
    render: renderCognitivePanel,
    renderCognitivePanel: renderCognitivePanelEntry,
    renderAttention: renderAttentionHeatmap,
    renderBelief: renderBeliefState,
    renderDiagnoses: renderDiagnoses,
    renderCouncil: renderCouncil,
    renderSimulation: renderSimulation,
    renderTrace: renderTrace,
    renderPlan: renderPlan
  };

})(typeof window !== "undefined" ? window : this);
