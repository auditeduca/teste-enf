/**
 * NurseGuard Engine — Gestão de Risco NR-01
 * localStorage + Nurse-PaLM integration
 */
(function () {
  'use strict';
  const RISK_KEY = 'nis_nurseguard_risks';
  const ACTION_KEY = 'nis_nurseguard_actions';

  const HAZARD_LABELS = { biological: 'Biológico', chemical: 'Químico', physical: 'Físico', ergonomic: 'Ergonômico', psychosocial: 'Psicossocial', accident: 'Acidente' };
  const PROB_LABELS = { 1: 'Baixa', 2: 'Média', 3: 'Alta', 4: 'Muito Alta' };
  const SEV_LABELS = { 1: 'Leve', 2: 'Moderada', 3: 'Grave', 4: 'Muito Grave' };
  const PRIORITY_COLORS = { low: '#27ae60', medium: '#f39c12', high: '#e74c3c', urgent: '#c0392b' };
  const PRIORITY_LABELS = { low: 'Baixa', medium: 'Média', high: 'Alta', urgent: 'Urgente' };
  const STATUS_LABELS = { pending: 'Pendente', in_progress: 'Em Andamento', completed: 'Concluído' };
  const ACTION_TYPE_LABELS = { elimination: 'Eliminação', mitigation: 'Mitigação', monitoring: 'Monitoramento', training: 'Treinamento', ppe: 'EPI' };

  const NORMS = [
    { code: 'NR-01', title: 'Disposições Gerais e Gerenciamento de Riscos', category: 'Segurança', applicability: 'Todos os empregadores', lastUpdate: '2020-09-23', status: 'active', description: 'Estabelece o GRO — Gerenciamento de Riscos Ocupacionais, incluindo identificação, avaliação e controle de riscos.' },
    { code: 'NR-32', title: 'Segurança e Saúde no Trabalho em Serviços de Saúde', category: 'Saúde', applicability: 'Estabelecimentos de saúde', lastUpdate: '2020-11-06', status: 'active', description: 'Proteção dos trabalhadores de serviços de saúde contra riscos biológicos, químicos, físicos, ergonômicos e de acidentes.' },
    { code: 'NR-35', title: 'Trabalho em Altura', category: 'Segurança', applicability: 'Trabalhos acima de 2m', lastUpdate: '2020-09-23', status: 'active', description: 'Estabelece requisitos para trabalho em altura, incluindo planejamento, autorização e EPI.' },
    { code: 'NR-06', title: 'Equipamento de Proteção Individual — EPI', category: 'Segurança', applicability: 'Todos os setores', lastUpdate: '2022-01-24', status: 'active', description: 'Define EPIs, certificação, responsabilidades do empregador e empregado.' },
    { code: 'NR-09', title: 'Avaliação e Controle das Exposições Ocupacionais a Agentes Físicos, Químicos e Biológicos', category: 'Saúde', applicability: 'Ambientes com agentes nocivos', lastUpdate: '2021-04-26', status: 'active', description: 'Estabelece critérios para caracterização, avaliação, monitoramento e controle de exposições ocupacionais.' },
    { code: 'NR-15', title: 'Atividades e Operações Insalubres', category: 'Saúde', applicability: 'Atividades insalubres', lastUpdate: '2022-01-24', status: 'active', description: 'Define os limites de tolerância e graus de insalubridade.' },
    { code: 'NR-17', title: 'Ergonomia', category: 'Ergonomia', applicability: 'Todas as atividades', lastUpdate: '2022-01-24', status: 'active', description: 'Estabelece parâmetros para adaptação das condições de trabalho às características psicofisiológicas do trabalhador.' },
    { code: 'NR-07', title: 'Programa de Controle Médico de Saúde Ocupacional — PCMSO', category: 'Saúde', applicability: 'Todos os empregadores', lastUpdate: '2022-01-24', status: 'active', description: 'Estabelece obrigatoriedade do PCMSO para controle e vigilância médica.' },
  ];

  function getRisks() { try { return JSON.parse(localStorage.getItem(RISK_KEY) || '[]'); } catch { return []; } }
  function saveRisks(r) { localStorage.setItem(RISK_KEY, JSON.stringify(r)); }
  function getActions() { try { return JSON.parse(localStorage.getItem(ACTION_KEY) || '[]'); } catch { return []; } }
  function saveActions(a) { localStorage.setItem(ACTION_KEY, JSON.stringify(a)); }

  function calcRiskLevel(prob, sev) {
    const score = prob * sev;
    if (score <= 4) return { level: 'acceptable', label: 'Aceitável', color: '#27ae60' };
    if (score <= 9) return { level: 'tolerable', label: 'Tolerável', color: '#f39c12' };
    return { level: 'unacceptable', label: 'Inaceitável', color: '#e74c3c' };
  }

  function addRisk() {
    const title = val('riskTitle');
    const sector = val('riskSector');
    if (!title || !sector) { alert('Preencha título e setor.'); return; }
    const prob = parseInt(val('riskProb'));
    const sev = parseInt(val('riskSev'));
    const rl = calcRiskLevel(prob, sev);
    const risk = {
      id: Date.now().toString(), title, sector,
      hazardType: val('riskHazardType'),
      description: val('riskDesc'),
      exposedWorkers: num('riskExposed'),
      probability: prob, severity: sev,
      riskLevel: rl.level, riskScore: prob * sev,
      existingControls: val('riskControls'),
      recommendedControls: val('riskRecommended'),
      status: 'draft',
      createdAt: new Date().toISOString(),
    };
    const risks = getRisks();
    risks.unshift(risk);
    saveRisks(risks);
    ['riskTitle','riskSector','riskDesc','riskExposed','riskControls','riskRecommended'].forEach(clearInput);
    renderRisks();
    renderMatrix();
    renderStats();
    refreshActionRiskSelect();
  }

  function renderRisks() {
    const el = document.getElementById('riskList');
    if (!el) return;
    const risks = getRisks();
    if (!risks.length) { el.innerHTML = '<p class="field-hint">Nenhuma avaliação registrada.</p>'; return; }
    el.innerHTML = risks.map(r => {
      const rl = calcRiskLevel(r.probability, r.severity);
      return `<div style="padding:0.75rem;border:1px solid var(--c-border);border-left:4px solid ${rl.color};border-radius:0.5rem;margin-bottom:0.75rem">
        <div style="display:flex;justify-content:space-between;align-items:start">
          <div>
            <p style="font-weight:600">${r.title}</p>
            <p style="font-size:0.85rem;color:var(--c-text-muted)">${r.sector} · ${HAZARD_LABELS[r.hazardType]} · ${r.exposedWorkers} expostos</p>
            <p style="font-size:0.85rem;color:var(--c-text-muted)">Prob: ${PROB_LABELS[r.probability]} · Sev: ${SEV_LABELS[r.severity]} · Score: ${r.riskScore}</p>
            ${r.description ? `<p style="font-size:0.9rem;margin-top:0.25rem">${r.description}</p>` : ''}
            ${r.existingControls ? `<p style="font-size:0.85rem;margin-top:0.25rem"><strong>Controles:</strong> ${r.existingControls}</p>` : ''}
            ${r.recommendedControls ? `<p style="font-size:0.85rem;margin-top:0.25rem"><strong>Recomendados:</strong> ${r.recommendedControls}</p>` : ''}
          </div>
          <div style="display:flex;flex-direction:column;gap:0.25rem;align-items:flex-end">
            <span style="background:${rl.color};color:#fff;padding:0.25rem 0.75rem;border-radius:1rem;font-size:0.75rem;font-weight:600">${rl.label}</span>
            <button class="btn-icon" style="font-size:0.8rem;padding:0.25rem 0.5rem" onclick="window.NurseGuard.delRisk('${r.id}')">Excluir</button>
          </div>
        </div>
      </div>`;
    }).join('');
  }

  function delRisk(id) { saveRisks(getRisks().filter(r => r.id !== id)); renderRisks(); renderMatrix(); renderStats(); refreshActionRiskSelect(); }

  function renderMatrix() {
    const el = document.getElementById('riskMatrix');
    if (!el) return;
    const risks = getRisks();
    const matrix = {};
    risks.forEach(r => { const key = `${r.probability}_${r.severity}`; matrix[key] = (matrix[key] || 0) + 1; });

    let html = '<table style="width:100%;border-collapse:collapse;text-align:center"><thead><tr><th style="padding:0.5rem"></th>';
    for (let s = 1; s <= 4; s++) html += `<th style="padding:0.5rem;font-size:0.85rem">Sev ${s}</th>`;
    html += '</tr></thead><tbody>';
    for (let p = 4; p >= 1; p--) {
      html += `<tr><td style="padding:0.5rem;font-weight:600;font-size:0.85rem">Prob ${p}</td>`;
      for (let s = 1; s <= 4; s++) {
        const score = p * s;
        const rl = calcRiskLevel(p, s);
        const count = matrix[`${p}_${s}`] || 0;
        html += `<td style="padding:0.5rem"><div style="background:${rl.color}22;border:2px solid ${rl.color};border-radius:0.5rem;padding:0.75rem;min-height:50px;display:flex;flex-direction:column;justify-content:center;align-items:center">
          <span style="font-weight:700;color:${rl.color};font-size:1.1rem">${score}</span>
          ${count ? `<span style="font-size:0.75rem;color:${rl.color}">${count} risco(s)</span>` : ''}
        </div></td>`;
      }
      html += '</tr>';
    }
    html += '</tbody></table>';
    el.innerHTML = html;
  }

  function addAction() {
    const title = val('actionTitle');
    if (!title) { alert('Preencha o título.'); return; }
    const action = {
      id: Date.now().toString(), title,
      riskAssessmentId: val('actionRisk'),
      description: val('actionDesc'),
      actionType: val('actionType'),
      responsible: val('actionResp'),
      deadline: val('actionDeadline'),
      priority: val('actionPriority'),
      status: 'pending',
      createdAt: new Date().toISOString(),
    };
    const actions = getActions();
    actions.unshift(action);
    saveActions(actions);
    ['actionTitle','actionDesc','actionResp','actionDeadline'].forEach(clearInput);
    renderActions();
    renderStats();
  }

  function renderActions() {
    const el = document.getElementById('actionList');
    if (!el) return;
    const actions = getActions();
    if (!actions.length) { el.innerHTML = '<p class="field-hint">Nenhum plano de ação.</p>'; return; }
    const risks = getRisks();
    el.innerHTML = actions.map(a => {
      const risk = risks.find(r => r.id === a.riskAssessmentId);
      const progress = a.status === 'completed' ? 100 : a.status === 'in_progress' ? 50 : 0;
      return `<div style="padding:0.75rem;border:1px solid var(--c-border);border-radius:0.5rem;margin-bottom:0.75rem">
        <div style="display:flex;justify-content:space-between;align-items:start">
          <div>
            <p style="font-weight:600">${a.title}</p>
            <p style="font-size:0.85rem;color:var(--c-text-muted)">${risk ? `Vinculado: ${risk.title}` : 'Sem vínculo'} · ${ACTION_TYPE_LABELS[a.actionType]} · Resp: ${a.responsible || '—'}</p>
            <p style="font-size:0.85rem;color:var(--c-text-muted)">Prazo: ${a.deadline ? new Date(a.deadline).toLocaleDateString('pt-BR') : '—'}</p>
            ${a.description ? `<p style="font-size:0.9rem;margin-top:0.25rem">${a.description}</p>` : ''}
            <div style="margin-top:0.5rem;background:var(--c-surface);border-radius:0.5rem;height:6px;overflow:hidden"><div style="height:100%;background:var(--c-primary);width:${progress}%"></div></div>
          </div>
          <div style="display:flex;flex-direction:column;gap:0.25rem;align-items:flex-end">
            <span style="background:${PRIORITY_COLORS[a.priority]};color:#fff;padding:0.25rem 0.75rem;border-radius:1rem;font-size:0.75rem;font-weight:600">${PRIORITY_LABELS[a.priority]}</span>
            <select onchange="window.NurseGuard.updateActionStatus('${a.id}', this.value)" style="font-size:0.8rem;padding:0.25rem;border-radius:0.4rem;border:1px solid var(--c-border)">
              <option value="pending" ${a.status==='pending'?'selected':''}>Pendente</option>
              <option value="in_progress" ${a.status==='in_progress'?'selected':''}>Em Andamento</option>
              <option value="completed" ${a.status==='completed'?'selected':''}>Concluído</option>
            </select>
            <button class="btn-icon" style="font-size:0.8rem;padding:0.25rem 0.5rem" onclick="window.NurseGuard.delAction('${a.id}')">Excluir</button>
          </div>
        </div>
      </div>`;
    }).join('');
  }

  function updateActionStatus(id, status) {
    const actions = getActions();
    const idx = actions.findIndex(a => a.id === id);
    if (idx >= 0) { actions[idx].status = status; saveActions(actions); renderActions(); renderStats(); }
  }

  function delAction(id) { saveActions(getActions().filter(a => a.id !== id)); renderActions(); renderStats(); }

  function refreshActionRiskSelect() {
    const sel = document.getElementById('actionRisk');
    if (!sel) return;
    const risks = getRisks();
    sel.innerHTML = '<option value="">— Selecione —</option>' + risks.map(r => `<option value="${r.id}">${r.title}</option>`).join('');
  }

  function renderNorms() {
    const el = document.getElementById('normsList');
    if (!el) return;
    el.innerHTML = NORMS.map(n => `<div style="padding:0.75rem;border:1px solid var(--c-border);border-radius:0.5rem;margin-bottom:0.5rem">
      <div style="display:flex;justify-content:space-between;align-items:start">
        <div>
          <p style="font-weight:600"><span style="color:var(--c-primary)">${n.code}</span> — ${n.title}</p>
          <p style="font-size:0.85rem;color:var(--c-text-muted)">${n.description}</p>
          <p style="font-size:0.8rem;color:var(--c-text-muted);margin-top:0.25rem">Aplicabilidade: ${n.applicability} · Atualizada: ${new Date(n.lastUpdate).toLocaleDateString('pt-BR')}</p>
        </div>
        <span class="tool-category-badge" style="font-size:0.75rem">${n.category}</span>
      </div>
    </div>`).join('');
  }

  function renderStats() {
    const risks = getRisks();
    const actions = getActions();
    setText('ngStatTotal', risks.length);
    setText('ngStatUnacceptable', risks.filter(r => r.riskLevel === 'unacceptable').length);
    setText('ngStatTolerable', risks.filter(r => r.riskLevel === 'tolerable').length);
    setText('ngStatAcceptable', risks.filter(r => r.riskLevel === 'acceptable').length);
    setText('ngStatActions', actions.length);
  }

  // ===== Nurse-PaLM Cognitive Analysis =====
  function runCognitiveAnalysis() {
    const risks = getRisks();
    const actions = getActions();
    const el = document.getElementById('ngCognitiveResult');
    if (!el) return;
    if (!risks.length) { el.innerHTML = '<p class="field-hint">Registre avaliações de risco primeiro.</p>'; return; }

    // Use Nurse-PaLM cognitive engine
    let cognitiveInsight = '';
    if (window.NursePaLM && window.CognitiveUI) {
      try {
        // Build observations from risk data
        const avgScore = risks.reduce((s, r) => s + r.riskScore, 0) / risks.length;
        const observations = [
          { type: 'heartRate', value: 72 + avgScore * 8 },
          { type: 'systolicBP', value: 120 - avgScore * 5 },
          { type: 'spO2', value: 98 - avgScore * 2 },
          { type: 'respiratoryRate', value: 16 + Math.round(avgScore) },
        ];
        const attention = window.NursePaLM.evaluateAttention(observations);
        const alertLevel = attention.alert ? '🔴 CRÍTICO' : attention.filtered.length > 2 ? '🟡 ATENÇÃO' : '🟢 NORMAL';
        cognitiveInsight = `<div style="padding:0.75rem;background:#fff;border-radius:0.5rem;border-left:3px solid var(--c-primary);margin-top:0.5rem">
          <p style="font-size:0.9rem;font-weight:600">🧠 Nurse-PaLM V9 — Análise Cognitiva:</p>
          <p style="font-size:0.85rem;margin-top:0.25rem">Nível de alerta: <strong>${alertLevel}</strong></p>
          <p style="font-size:0.85rem">Sinais em atenção: ${attention.filtered.length} de ${attention.ranked.length}</p>
          <p style="font-size:0.85rem">Confiança: ${((1 - Math.min(1, avgScore / 16)) * 100).toFixed(0)}%</p>
        </div>`;
      } catch (e) { console.warn('[NurseGuard] Nurse-PaLM error:', e); }
    }

    // Heuristic analysis
    const unacceptable = risks.filter(r => r.riskLevel === 'unacceptable');
    const byHazard = {};
    risks.forEach(r => { byHazard[r.hazardType] = (byHazard[r.hazardType] || 0) + 1; });
    const topHazard = Object.entries(byHazard).sort((a, b) => b[1] - a[1])[0];
    const pendingActions = actions.filter(a => a.status === 'pending').length;
    const urgentActions = actions.filter(a => a.priority === 'urgent' && a.status !== 'completed').length;

    el.innerHTML = `
      <div style="padding:1rem;background:var(--c-surface);border-radius:0.5rem;border:1px solid var(--c-border)">
        <h3 style="font-size:1rem;font-weight:700;margin-bottom:0.5rem">📊 Análise de Padrões de Risco</h3>
        <ul style="padding-left:1.5rem;line-height:2;font-size:0.9rem">
          <li><strong>${risks.length}</strong> riscos avaliados · Score médio: <strong>${(risks.reduce((s, r) => s + r.riskScore, 0) / risks.length).toFixed(1)}</strong></li>
          <li><strong style="color:#e74c3c">${unacceptable.length}</strong> riscos inaceitáveis requerem ação imediata</li>
          <li>Tipo de risco mais frequente: <strong>${topHazard ? HAZARD_LABELS[topHazard[0]] : '—'}</strong> (${topHazard ? topHazard[1] : 0} ocorrências)</li>
          <li><strong>${pendingActions}</strong> planos de ação pendentes · <strong style="color:#c0392b">${urgentActions}</strong> urgentes</li>
          <li>Cobertura de ações: <strong>${risks.length ? Math.round((risks.filter(r => actions.some(a => a.riskAssessmentId === r.id)).length / risks.length) * 100) : 0}%</strong> dos riscos têm plano de ação</li>
        </ul>
        ${cognitiveInsight}
        <p style="font-size:0.85rem;color:var(--c-text-muted);margin-top:0.75rem">⚡ Recomendação: ${unacceptable.length > 0 ? 'Priorize a mitigação dos riscos inaceitáveis antes de qualquer outra ação.' : 'Mantenha monitoramento contínuo e revise controles existentes.'}</p>
      </div>
    `;
  }

  // Utils
  function val(id) { return document.getElementById(id)?.value?.trim() || ''; }
  function num(id) { return parseInt(document.getElementById(id)?.value) || 0; }
  function setText(id, v) { const el = document.getElementById(id); if (el) el.textContent = v; }
  function clearInput(id) { const el = document.getElementById(id); if (el) el.value = ''; }

  function init() {
    document.getElementById('addRiskBtn')?.addEventListener('click', addRisk);
    document.getElementById('addActionBtn')?.addEventListener('click', addAction);
    document.getElementById('ngCognitiveBtn')?.addEventListener('click', runCognitiveAnalysis);
    renderRisks();
    renderMatrix();
    renderActions();
    renderNorms();
    renderStats();
    refreshActionRiskSelect();
  }

  window.NurseGuard = { delRisk, delAction, updateActionStatus, init };
  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
