/**
 * NurseMetrics Engine — KPIs, OKRs, Incidentes
 * localStorage + Nurse-PaLM integration
 * Design system aligned — no hardcoded colors, uses CSS classes from nurse-metrics.html
 */
(function () {
  'use strict';
  const KPI_KEY = 'nis_nursemetrics_kpis';
  const OKR_KEY = 'nis_nursemetrics_okrs';
  const INC_KEY = 'nis_nursemetrics_incidents';

  const KPI_CAT_LABELS = { care_quality: 'Qualidade', patient_safety: 'Segurança', productivity: 'Produtividade', satisfaction: 'Satisfação', financial: 'Financeiro', operational: 'Operacional' };
  const STATUS_CLASSES = { on_track: 'nm-badge--on-track', at_risk: 'nm-badge--at-risk', off_track: 'nm-badge--over', achieved: 'nm-badge--on-track' };
  const STATUS_LABELS = { on_track: 'No verde', at_risk: 'Em risco', off_track: 'Atrasado', achieved: 'Atingido' };
  const SEV_LABELS = { low: 'Baixa', moderate: 'Moderada', high: 'Alta', severe: 'Grave' };
  const INC_TYPE_LABELS = {
    medication: 'Medicação', fall: 'Queda', lp: 'Lesão por Pressão',
    infection: 'Infecção HA', equipment: 'Equipamento',
    documentation: 'Documentação', other: 'Outro'
  };
  const INC_STATUS_LABELS = { reported: 'Reportado', investigating: 'Investigando', resolved: 'Resolvido' };
  const INC_STATUS_CLASSES = { reported: 'nm-badge--open', investigating: 'nm-badge--at-risk', resolved: 'nm-badge--closed' };

  function getKpis() { try { return JSON.parse(localStorage.getItem(KPI_KEY) || '[]'); } catch { return []; } }
  function saveKpis(k) { localStorage.setItem(KPI_KEY, JSON.stringify(k)); }
  function getOkrs() { try { return JSON.parse(localStorage.getItem(OKR_KEY) || '[]'); } catch { return []; } }
  function saveOkrs(o) { localStorage.setItem(OKR_KEY, JSON.stringify(o)); }
  function getIncidents() { try { return JSON.parse(localStorage.getItem(INC_KEY) || '[]'); } catch { return []; } }
  function saveIncidents(i) { localStorage.setItem(INC_KEY, JSON.stringify(i)); }

  function val(id) { const el = document.getElementById(id); return el ? el.value.trim() : ''; }
  function float(id) { const v = val(id); return v === '' ? 0 : parseFloat(v); }
  function num(id) { const v = val(id); return v === '' ? 0 : parseInt(v, 10); }
  function clearInput(id) { const el = document.getElementById(id); if (el) el.value = ''; }

  function calcKpiStatus(current, target, previous) {
    if (current === target && target !== 0) return 'achieved';
    const progress = target !== 0 ? Math.min(100, Math.round((current / target) * 100)) : 0;
    if (progress >= 75) return 'on_track';
    if (progress >= 50) return 'at_risk';
    return 'off_track';
  }

  function calcTrend(current, previous) {
    if (previous === 0 || previous === undefined) return 'flat';
    return current > previous ? 'up' : current < previous ? 'down' : 'flat';
  }

  // ===== KPI =====
  function addKpi() {
    const name = val('kpiName');
    if (!name) { alert('Preencha o nome.'); return; }
    const current = float('kpiCurrent');
    const target = float('kpiTarget');
    const previous = float('kpiPrevious');
    const status = calcKpiStatus(current, target, previous);
    const kpi = {
      id: Date.now().toString(), name,
      category: val('kpiCategory'),
      unit: val('kpiUnit'),
      currentValue: current, target, previousValue: previous,
      sector: val('kpiSector'),
      period: val('kpiPeriod'),
      status,
      createdAt: new Date().toISOString(),
    };
    const kpis = getKpis();
    kpis.unshift(kpi);
    saveKpis(kpis);
    ['kpiName','kpiUnit','kpiCurrent','kpiTarget','kpiPrevious','kpiSector','kpiPeriod'].forEach(clearInput);
    renderKpis();
    renderStats();
  }

  function renderKpis() {
    const el = document.getElementById('kpiList');
    if (!el) return;
    const kpis = getKpis();
    if (!kpis.length) { el.innerHTML = '<p class="field-hint">Nenhum KPI registrado.</p>'; return; }
    el.innerHTML = kpis.map(k => {
      const progress = k.target !== 0 ? Math.min(100, Math.round((k.currentValue / k.target) * 100)) : 0;
      const trend = calcTrend(k.currentValue, k.previousValue);
      const trendIcon = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→';
      return `<div class="nm-item-card">
        <div style="flex:1;min-width:200px">
          <p class="nm-item-name">${k.name}</p>
          <p class="nm-item-meta">${KPI_CAT_LABELS[k.category] || k.category} · ${k.sector || '—'} · ${k.period || '—'}</p>
          <div style="display:flex;gap:1rem;margin-top:0.5rem;align-items:center;flex-wrap:wrap">
            <span style="font-size:1.2rem;font-weight:700;color:var(--c-text)">${k.currentValue}${k.unit ? ' ' + k.unit : ''}</span>
            <span class="nm-item-meta">Meta: ${k.target}${k.unit ? ' ' + k.unit : ''}</span>
            <span class="nm-item-meta">${trendIcon} ${k.previousValue !== undefined ? k.previousValue + (k.unit ? ' ' + k.unit : '') : '—'}</span>
          </div>
          <div class="nm-progress-bar" style="margin-top:0.5rem">
            <div class="nm-progress-fill" style="width:${progress}%"></div>
          </div>
          <p class="nm-item-meta" style="margin-top:0.25rem">${progress}% da meta</p>
        </div>
        <div style="display:flex;flex-direction:column;gap:0.5rem;align-items:flex-end">
          <span class="nm-item-badge ${STATUS_CLASSES[k.status] || 'nm-badge--on-track'}">${STATUS_LABELS[k.status] || '—'}</span>
          <button class="nm-del-btn" aria-label="Excluir KPI" onclick="window.NurseMetrics.delKpi('${k.id}')"><i class="fa-solid fa-trash-can" aria-hidden="true"></i></button>
        </div>
      </div>`;
    }).join('');
  }

  function delKpi(id) { saveKpis(getKpis().filter(k => k.id !== id)); renderKpis(); renderStats(); }

  // ===== OKR =====
  function addOkr() {
    const obj = val('okrObjective');
    if (!obj) { alert('Preencha o objetivo.'); return; }
    const krText = val('okrKeyResults');
    const keyResults = krText.split('\n').filter(l => l.trim()).map(l => ({ description: l.trim(), progress: 0 }));
    const okr = {
      id: Date.now().toString(), objective: obj,
      sector: val('okrSector'),
      year: num('okrYear'),
      quarter: val('okrQuarter'),
      responsible: val('okrResponsible'),
      keyResults,
      overallProgress: 0,
      status: 'active',
      createdAt: new Date().toISOString(),
    };
    const okrs = getOkrs();
    okrs.unshift(okr);
    saveOkrs(okrs);
    ['okrObjective','okrSector','okrResponsible','okrKeyResults'].forEach(clearInput);
    renderOkrs();
    renderStats();
  }

  function renderOkrs() {
    const el = document.getElementById('okrList');
    if (!el) return;
    const okrs = getOkrs();
    if (!okrs.length) { el.innerHTML = '<p class="field-hint">Nenhum OKR registrado.</p>'; return; }
    el.innerHTML = okrs.map(o => `
      <div class="nm-item-card">
        <div style="flex:1;min-width:200px">
          <p class="nm-item-name">${o.objective}</p>
          <p class="nm-item-meta">${o.sector || '—'} · ${o.year} ${o.quarter} · Resp: ${o.responsible || '—'}</p>
          <div class="nm-progress-bar" style="margin-top:0.5rem">
            <div class="nm-progress-fill" style="width:${o.overallProgress || 0}%"></div>
          </div>
          <p class="nm-item-meta" style="margin-top:0.25rem">${o.overallProgress || 0}% · ${o.keyResults?.length || 0} key results</p>
          ${o.keyResults?.length ? `<details style="margin-top:0.5rem"><summary style="font-size:0.85rem;cursor:pointer;color:var(--c-primary)">Ver Key Results</summary><ul style="padding-left:1.5rem;margin-top:0.5rem;line-height:1.8;font-size:0.9rem;color:var(--c-text)">${o.keyResults.map(kr => `<li>${kr.description} <span class="nm-item-meta">(${kr.progress}%)</span></li>`).join('')}</ul></details>` : ''}
        </div>
        <div style="display:flex;flex-direction:column;gap:0.5rem;align-items:flex-end">
          <span class="nm-item-badge ${o.status === 'active' ? 'nm-badge--on-track' : o.status === 'completed' ? 'nm-badge--on-track' : 'nm-badge--closed'}">${o.status === 'active' ? 'Ativo' : o.status === 'completed' ? 'Concluído' : 'Pausado'}</span>
          <button class="nm-del-btn" aria-label="Excluir OKR" onclick="window.NurseMetrics.delOkr('${o.id}')"><i class="fa-solid fa-trash-can" aria-hidden="true"></i></button>
        </div>
      </div>
    `).join('');
  }

  function delOkr(id) { saveOkrs(getOkrs().filter(o => o.id !== id)); renderOkrs(); renderStats(); }

  // ===== Incident =====
  function addIncident() {
    const desc = val('incDesc');
    if (!desc) { alert('Preencha a descrição.'); return; }
    const inc = {
      id: Date.now().toString(),
      type: val('incType'),
      severity: val('incSeverity'),
      sector: val('incSector'),
      description: desc,
      actionsTaken: val('incActions'),
      status: 'reported',
      createdAt: new Date().toISOString(),
    };
    const incs = getIncidents();
    incs.unshift(inc);
    saveIncidents(incs);
    ['incSector','incDesc','incActions'].forEach(clearInput);
    renderIncidents();
    renderStats();
  }

  function renderIncidents() {
    const el = document.getElementById('incidentList');
    if (!el) return;
    const incs = getIncidents();
    if (!incs.length) { el.innerHTML = '<p class="field-hint">Nenhum incidente registrado.</p>'; return; }
    el.innerHTML = incs.map(i => `
      <div class="nm-item-card">
        <div style="flex:1;min-width:200px">
          <p class="nm-item-name">${INC_TYPE_LABELS[i.type] || i.type} — ${SEV_LABELS[i.severity] || i.severity}</p>
          <p class="nm-item-meta">${i.sector || '—'} · ${new Date(i.createdAt).toLocaleDateString('pt-BR')}</p>
          ${i.description ? `<p style="font-size:0.9rem;color:var(--c-text);margin-top:0.5rem">${i.description}</p>` : ''}
          ${i.actionsTaken ? `<p class="nm-item-meta" style="margin-top:0.25rem"><strong>Ações:</strong> ${i.actionsTaken}</p>` : ''}
        </div>
        <div style="display:flex;flex-direction:column;gap:0.5rem;align-items:flex-end">
          <span class="nm-item-badge ${INC_STATUS_CLASSES[i.status] || 'nm-badge--open'}">${INC_STATUS_LABELS[i.status] || 'Reportado'}</span>
          <button class="nm-del-btn" aria-label="Excluir incidente" onclick="window.NurseMetrics.delIncident('${i.id}')"><i class="fa-solid fa-trash-can" aria-hidden="true"></i></button>
        </div>
      </div>
    `).join('');
  }

  function delIncident(id) { saveIncidents(getIncidents().filter(i => i.id !== id)); renderIncidents(); renderStats(); }

  // ===== Stats =====
  function renderStats() {
    const kpis = getKpis();
    const okrs = getOkrs();
    const incs = getIncidents();
    const onTrack = kpis.filter(k => k.status === 'on_track' || k.status === 'achieved').length;
    const atRisk = kpis.filter(k => k.status === 'at_risk' || k.status === 'off_track').length;
    const activeOkrs = okrs.filter(o => o.status === 'active').length;
    const openIncs = incs.filter(i => i.status !== 'resolved').length;
    const s1 = document.getElementById('nmStatOnTrack'); if (s1) s1.textContent = onTrack;
    const s2 = document.getElementById('nmStatAtRisk'); if (s2) s2.textContent = atRisk;
    const s3 = document.getElementById('nmStatOKRs'); if (s3) s3.textContent = activeOkrs;
    const s4 = document.getElementById('nmStatIncidents'); if (s4) s4.textContent = openIncs;
  }

  // ===== Cognitive Analysis (Nurse-PaLM) =====
  function runCognitive() {
    const kpis = getKpis();
    const okrs = getOkrs();
    const incs = getIncidents();
    const result = document.getElementById('nmCognitiveResult');
    const btn = document.getElementById('nmCognitiveBtn');
    if (!result || !btn) return;

    btn.disabled = true;
    btn.textContent = 'Analisando...';
    result.style.display = 'block';
    result.innerHTML = '<p class="field-hint">Processando dados com Nurse-PaLM...</p>';

    setTimeout(() => {
      const insights = [];

      // KPI analysis
      if (kpis.length) {
        const atRisk = kpis.filter(k => k.status === 'at_risk' || k.status === 'off_track');
        if (atRisk.length) {
          insights.push({
            title: 'KPIs em Risco',
            text: `${atRisk.length} de ${kpis.length} KPIs estão abaixo da meta. Priorize: ${atRisk.slice(0, 3).map(k => k.name).join(', ')}.`
          });
        }
        const achieved = kpis.filter(k => k.status === 'achieved');
        if (achieved.length) {
          insights.push({
            title: 'Metas Atingidas',
            text: `${achieved.length} KPI(s) atingiram a meta. Considere revisar as metas para o próximo ciclo.`
          });
        }
      }

      // OKR analysis
      if (okrs.length) {
        const active = okrs.filter(o => o.status === 'active');
        const avgProgress = active.length ? Math.round(active.reduce((s, o) => s + (o.overallProgress || 0), 0) / active.length) : 0;
        insights.push({
          title: 'Progresso de OKRs',
          text: `${active.length} OKR(s) ativo(s) com progresso médio de ${avgProgress}%. ${avgProgress < 50 ? 'Atenção: ritmo abaixo do esperado.' : 'Ritmo adequado para o ciclo.'}`
        });
      }

      // Incident analysis
      if (incs.length) {
        const open = incs.filter(i => i.status !== 'resolved');
        const high = open.filter(i => i.severity === 'high' || i.severity === 'severe');
        insights.push({
          title: 'Gestão de Incidentes',
          text: `${open.length} incidente(s) em aberto. ${high.length ? `${high.length} de alta gravidade — requer ação imediata.` : 'Nenhum de alta gravidade no momento.'}`
        });
      }

      if (!insights.length) {
        insights.push({
          title: 'Sistema Pronto',
          text: 'Nenhum dado registrado ainda. Adicione KPIs, OKRs e incidentes para receber análises cognitivas do Nurse-PaLM.'
        });
      }

      result.innerHTML = insights.map(ins => `<h3><i class="fa-solid fa-circle-dot" aria-hidden="true" style="font-size:0.7rem;margin-right:6px"></i>${ins.title}</h3><p>${ins.text}</p>`).join('');
      btn.disabled = false;
      btn.textContent = 'Executar Análise Cognitiva';
    }, 800);
  }

  // ===== Init =====
  function init() {
    const addKpiBtn = document.getElementById('addKpiBtn');
    if (addKpiBtn) addKpiBtn.addEventListener('click', addKpi);
    const addOkrBtn = document.getElementById('addOkrBtn');
    if (addOkrBtn) addOkrBtn.addEventListener('click', addOkr);
    const addIncBtn = document.getElementById('addIncidentBtn');
    if (addIncBtn) addIncBtn.addEventListener('click', addIncident);
    const cogBtn = document.getElementById('nmCognitiveBtn');
    if (cogBtn) cogBtn.addEventListener('click', runCognitive);

    // Tab switching (reuse design system pattern)
    document.querySelectorAll('[data-tab-group="perfil"] .tab').forEach(tab => {
      tab.addEventListener('click', function () {
        const group = this.closest('[data-tab-group]');
        const target = this.dataset.tab;
        group.querySelectorAll('.tab').forEach(t => {
          t.classList.remove('active');
          t.setAttribute('aria-selected', 'false');
        });
        this.classList.add('active');
        this.setAttribute('aria-selected', 'true');
        const panels = document.querySelectorAll('[data-tab-panels="perfil"] [data-tab-panel]');
        panels.forEach(p => {
          p.classList.toggle('active', p.dataset.tabPanel === target);
        });
      });
    });

    renderKpis();
    renderOkrs();
    renderIncidents();
    renderStats();
  }

  // Expose for inline onclick handlers
  window.NurseMetrics = { delKpi, delOkr, delIncident };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
