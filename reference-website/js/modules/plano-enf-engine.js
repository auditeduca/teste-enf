/**
 * PlanoEnf Engine — Planos de Cuidado de Enfermagem
 * Site estático: usa localStorage para persistência
 * Integração: Nurse-PaLM (cognitive engine) para sugestões
 */
(function () {
  'use strict';

  // ===== Base de dados local (NANDA subset) =====
  const NANDA_DB = [
    { code: '00046', name: 'Risco de lesão por pressão', domain: 11, domainName: 'Resposta psicossocial', class: 2, definition: 'Vulnerabilidade a dano na epiderme e/ou derme.', characteristics: [], relatedFactors: ['Imobilização física', 'Redução da mobilidade', 'Sensibilidade alterada', 'Umidade da pele', 'Nutrição inadequada'], riskFactors: ['Imobilidade no leito', 'Incontinência urinária', 'Idade avançada', 'Déficit nutricional'], sctId: '417355001', icd11: '', evidenceGrade: 'B' },
    { code: '00004', name: 'Risco de infecção', domain: 11, domainName: 'Resposta psicossocial', class: 4, definition: 'Vulnerabilidade a invasão e multiplicação de organismos patogênicos.', characteristics: [], relatedFactors: [], riskFactors: ['Procedimento invasivo', 'Imunidade comprometida', 'Queimaduras', 'Cirurgia recente', 'Cateter venoso'], sctId: '441687005', icd11: '', evidenceGrade: 'A' },
    { code: '00032', name: 'Dor aguda', domain: 12, domainName: 'Resposta espiritual', class: 1, definition: 'Experiência sensorial e emocional desagradável associada a lesão tecidual real ou potencial.', characteristics: ['Relato verbal de dor', 'Expressão facial de dor', 'Conduta de proteção', 'Taquicardia', 'Hipertensão'], relatedFactors: ['Agente lesivo biológico', 'Agente lesivo químico', 'Agente lesivo físico', 'Isquemia'], riskFactors: [], sctId: '22253000', icd11: 'MG30', evidenceGrade: 'A' },
    { code: '00085', name: 'Mobilidade física prejudicada', domain: 4, domainName: 'Sistema cardiovascular', class: 4, definition: 'Limitação do movimento físico independente e intencional do corpo.', characteristics: ['Relutância em tentar movimento', 'Restrição de movimento imposta', 'Diminuição do ROM', 'Instabilidade na marcha'], relatedFactors: ['Redução de força muscular', 'Descondicionamento', 'Dor', 'Lesão neuromuscular'], riskFactors: [], sctId: '248248009', icd11: '', evidenceGrade: 'B' },
    { code: '00132', name: 'Dor crônica', domain: 12, domainName: 'Resposta espiritual', class: 1, definition: 'Experiência sensorial e emocional desagradável contínua ou recorrente por mais de 3 meses.', characteristics: ['Relato verbal de dor', 'Conduta de proteção', 'Distúrbio do sono', 'Fadiga', 'Depressão'], relatedFactors: ['Agente lesivo crônico', 'Doença crônica'], riskFactors: [], sctId: '82423001', icd11: 'MG30', evidenceGrade: 'B' },
    { code: '00106', name: 'Ansiedade', domain: 9, domainName: 'Resposta humana', class: 2, definition: 'Sensação vaga e desconfortável de preocupação ou apreensão.', characteristics: ['Inquietação', 'Insônia', 'Irritabilidade', 'Taquicardia', 'Sudorese'], relatedFactors: ['Estresse', 'Ameaça à autoestima', 'Mudança de papel social', 'Conflito interpessoal'], riskFactors: [], sctId: '48694002', icd11: 'MB21', evidenceGrade: 'B' },
    { code: '00039', name: 'Risco de aspiração', domain: 11, domainName: 'Resposta psicossocial', class: 4, definition: 'Vulnerabilidade à entrada de secreções gastrointestinais ou orofaríngeas nas vias aéreas.', characteristics: [], relatedFactors: [], riskFactors: ['Nível de consciência reduzido', 'Disfagia', 'Sonda gástrica', 'Refluxo gastroesofágico', 'Traqueostomia'], sctId: '417369009', icd11: '', evidenceGrade: 'B' },
    { code: '00023', name: 'Incontinência urinária', domain: 3, domainName: 'Sistema urinário', class: 1, definition: 'Perda involuntária de urina.', characteristics: ['Relato de perda urinária', 'Umidade perineal', 'Odor de urina'], relatedFactors: ['Fraqueza do assoalho pélvico', 'Hiperplasia prostática', 'Déficit cognitivo'], riskFactors: [], sctId: '72980009', icd11: '', evidenceGrade: 'C' },
    { code: '00015', name: 'Risco de constipação', domain: 2, domainName: 'Sistema digestivo', class: 2, definition: 'Vulnerabilidade à diminuição da frequência normal de evacuação.', characteristics: [], relatedFactors: [], riskFactors: ['Imobilidade', 'Dieta pobre em fibras', 'Ingestão hídrica insuficiente', 'Medicamentos opióides'], sctId: '197020008', icd11: '', evidenceGrade: 'C' },
    { code: '00093', name: 'Fadiga', domain: 4, domainName: 'Sistema cardiovascular', class: 4, definition: 'Sensação esmagadora e sustentada de exaustão e diminuição da capacidade de trabalho.', characteristics: ['Relato de falta de energia', 'Incapacidade de manter a rotina', 'Aumento da necessidade de repouso', 'Letargia'], relatedFactors: ['Estresse', 'Doença', 'Gravidez', 'Anemia'], riskFactors: [], sctId: '84229001', icd11: 'MG40', evidenceGrade: 'C' },
    { code: '00047', name: 'Risco de lesão corporal', domain: 11, domainName: 'Resposta psicossocial', class: 2, definition: 'Vulnerabilidade a dano tecidual em decorrência de condições ambientais.', characteristics: [], relatedFactors: [], riskFactors: ['Deficiência sensorial', 'Confusão', 'Ambiente inseguro', 'Uso de medicamentos sedativos'], sctId: '417429009', icd11: '', evidenceGrade: 'B' },
    { code: '00118', name: 'Ansiedade ante a morte', domain: 9, domainName: 'Resposta humana', class: 2, definition: 'Preocupação vaga e desconfortável relacionada à morte ou ao morrer.', characteristics: ['Preocupação com a morte', 'Medo do processo de morrer', 'Preocupação com entes queridos', 'Negação'], relatedFactors: ['Doença terminal', 'Perda iminente'], riskFactors: [], sctId: '', icd11: '', evidenceGrade: 'C' },
  ];

  // NIC→NANDA e NOC→NANDA linkages
  const NIC_LINKS = {
    '00046': [{ code: '2500', name: 'Manejo da pressão', activities: ['Avaliar pele a cada turno', 'Reposicionar a cada 2h', 'Usar superfície de suporte adequada', 'Manter pele limpa e seca'] }, { code: '3520', name: 'Cuidados com a pele', activities: ['Inspecionar pele diariamente', 'Aplicar hidratante', 'Evitar fricção'] }],
    '00004': [{ code: '6550', name: 'Proteção contra infecção', activities: ['Higiene das mãos', 'Técnica asséptica', 'Monitorar sinais de infecção', 'Trocar curativos'] }, { code: '6540', name: 'Controle de infecção', activities: ['Isolar quando indicado', 'Descarte adequado', 'Vigilância epidemiológica'] }],
    '00032': [{ code: '1400', name: 'Manejo da dor', activities: ['Avaliar dor com escala', 'Administrar analgésicos', 'Posicionamento confortável', 'Técnicas não-farmacológicas'] }, { code: '1410', name: 'Manejo da dor aguda', activities: ['Avaliar características da dor', 'Monitorar resposta analgésica', 'Educar sobre controle'] }],
    '00085': [{ code: '0840', name: 'Mobilização', activities: ['Exercícios de ROM', 'Transferências seguras', 'Deambulação assistida', 'Uso de dispositivos auxiliares'] }, { code: '0200', name: 'Exercícios de mobilidade', activities: ['Exercícios ativos/passivos', 'Fortalecimento progressivo'] }],
    '00132': [{ code: '1400', name: 'Manejo da dor', activities: ['Plano analgésico contínuo', 'Técnicas de relaxamento', 'Suporte psicológico'] }, { code: '2780', name: 'Manejo da energia', activities: ['Pacing de atividades', 'Priorização de tarefas', 'Repouso programado'] }],
    '00106': [{ code: '5820', name: 'Redução da ansiedade', activities: ['Escuta ativa', 'Técnicas de relaxamento', 'Ambiente tranquilo', 'Informação clara'] }, { code: '5230', name: 'Aumentar o enfrentamento', activities: ['Identificar gatilhos', 'Desenvolver estratégias', 'Suporte emocional'] }],
    '00039': [{ code: '3200', name: 'Precauções para aspiração', activities: ['Elevação da cabeceira 30°', 'Avaliar deglutição', 'Dieta texturada', 'Suction quando necessário'] }],
    '00023': [{ code: '0610', name: 'Manejo da incontinência urinária', activities: ['Treinamento vesical', 'Exercícios do assoalho pélvico', 'Acesso ao toalete', 'Absorventes adequados'] }],
    '00015': [{ code: '0450', name: 'Manejo da constipação', activities: ['Dieta rica em fibras', 'Aumentar ingestão hídrica', 'Estimular atividade física', 'Laxativos se necessário'] }],
    '00093': [{ code: '2780', name: 'Manejo da energia', activities: ['Avaliar nível de fadiga', 'Pacing de atividades', 'Repouso adequado', 'Nutrição apropriada'] }, { code: '0200', name: 'Exercícios de mobilidade', activities: ['Exercícios graduais', 'Tolerância monitorada'] }],
    '00047': [{ code: '6480', name: 'Manejo ambiental', activities: ['Remover obstáculos', 'Iluminação adequada', 'Barras de apoio', 'Avaliar segurança'] }],
    '00118': [{ code: '5270', name: 'Suporte emocional', activities: ['Escuta ativa', 'Presença terapêutica', 'Validar sentimentos', 'Encaminhar suporte espiritual'] }],
  };

  const NOC_LINKS = {
    '00046': [{ code: '1101', name: 'Integridade tissular: pele e mucosas', indicators: ['Temperatura da pele', 'Sensibilidade', 'Hidratação', 'Integridade'] }, { code: '0304', name: ' autocuidado: higiene', indicators: ['Higiene da pele', 'Higiene oral'] }],
    '00004': [{ code: '0703', name: 'Severidade da infecção', indicators: ['Temperatura corporal', 'Contagem de leucócitos', 'Sinais vitais'] }],
    '00032': [{ code: '1605', name: 'Controle da dor', indicators: ['Reconhece fatores causais', 'Usa analgésicos', 'Relata dor controlada', 'Nível de conforto'] }, { code: '2102', name: 'Nível de dor', indicators: ['Dor referida', 'Expressão facial', 'Tensão muscular'] }],
    '00085': [{ code: '0208', name: 'Mobilidade', indicators: ['Movimento articular', 'Movimento muscular', 'Transferência', 'Deambulação'] }],
    '00132': [{ code: '1605', name: 'Controle da dor', indicators: ['Relato de dor', 'Uso de recursos', 'Qualidade de vida'] }, { code: '0007', name: 'Resiliência', indicators: ['Enfrentamento', 'Suporte social'] }],
    '00106': [{ code: '1211', name: 'Nível de ansiedade', indicators: ['Inquietação', 'Insônia', 'Taquicardia', 'Irritabilidade'] }, { code: '1402', name: 'Controle da ansiedade', indicators: ['Identifica gatilhos', 'Usa técnicas', 'Busca ajuda'] }],
    '00039': [{ code: '0410', name: 'Estado respiratório: vias aéreas', indicators: ['Ausência de aspiração', 'Padrão respiratório', 'Sons respiratórios'] }],
    '00023': [{ code: '0503', name: 'Continência urinária', indicators: ['Reconhece necessidade', 'Retém urina', 'Esvazia bexiga'] }],
    '00015': [{ code: '0501', name: 'Eliminação intestinal', indicators: ['Frequência de evacuação', 'Consistência', 'Esforço'] }],
    '00093': [{ code: '0007', name: 'Resiliência', indicators: ['Energia', 'Motivação', 'Capacidade funcional'] }],
    '00047': [{ code: '1906', name: 'Segurança: ambiente físico do lar', indicators: ['Ambiente livre de riscos', 'Iluminação', 'Acessibilidade'] }],
    '00118': [{ code: '1305', name: 'Processo de adaptação psicosocial', indicators: ['Enfrentamento', 'Aceitação', 'Esperança'] }],
  };

  // ===== Estado da aplicação =====
  let selectedDx = null;
  let selectedNICs = [];
  let selectedNOCs = [];

  // ===== localStorage =====
  const STORAGE_KEY = 'nis_planoenf_plans';

  function getPlans() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); } catch { return []; }
  }
  function savePlans(plans) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(plans));
  }

  // ===== Render =====
  function renderDxResults(query, domain) {
    const container = document.getElementById('dxResults');
    if (!container) return;
    const q = (query || '').toLowerCase().trim();
    let filtered = NANDA_DB;
    if (domain) filtered = filtered.filter(d => String(d.domain) === domain);
    if (q) filtered = filtered.filter(d => d.name.toLowerCase().includes(q) || d.code.includes(q) || (d.domainName || '').toLowerCase().includes(q));
    if (!filtered.length) {
      container.innerHTML = '<p class="field-hint" style="padding:1rem 0">Nenhum diagnóstico encontrado.</p>';
      return;
    }
    container.innerHTML = filtered.map(d => `
      <div class="dx-item" role="option" tabindex="0" data-code="${d.code}" style="padding:0.75rem;border:1px solid var(--c-border);border-radius:0.5rem;margin-bottom:0.5rem;cursor:pointer" onmouseover="this.style.background='var(--c-surface-hover)'" onmouseout="this.style.background=''">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div>
            <span style="font-weight:600;color:var(--c-primary)">${d.code}</span>
            <span style="margin-left:0.5rem">${d.name}</span>
          </div>
          <span class="tool-category-badge" style="font-size:0.75rem">${d.domainName || 'Domínio ' + d.domain}</span>
        </div>
      </div>
    `).join('');

    container.querySelectorAll('.dx-item').forEach(item => {
      item.addEventListener('click', () => selectDx(item.dataset.code));
      item.addEventListener('keydown', e => { if (e.key === 'Enter') selectDx(item.dataset.code); });
    });
  }

  function selectDx(code) {
    selectedDx = NANDA_DB.find(d => d.code === code);
    if (!selectedDx) return;
    selectedNICs = [];
    selectedNOCs = [];
    renderDxDetail();
    renderNIC();
    renderNOC();
    updatePlanSummary();
  }

  function renderDxDetail() {
    const el = document.getElementById('dxDetail');
    if (!el || !selectedDx) return;
    const d = selectedDx;
    el.innerHTML = `
      <div style="padding:1rem 0">
        <h3 style="font-size:1.1rem;margin-bottom:0.25rem">${d.code} — ${d.name}</h3>
        <p style="color:var(--c-text-muted);font-size:0.9rem;margin-bottom:0.75rem">Domínio ${d.domain} · Classe ${d.class}</p>
        <p style="margin-bottom:0.75rem;line-height:1.6">${d.definition}</p>
        ${d.characteristics.length ? `<p style="font-weight:600;margin-top:0.75rem">Características Definidoras:</p><ul style="padding-left:1.5rem;line-height:1.8">${d.characteristics.map(c => `<li>${c}</li>`).join('')}</ul>` : ''}
        ${d.relatedFactors.length ? `<p style="font-weight:600;margin-top:0.75rem">Fatores Relacionados:</p><ul style="padding-left:1.5rem;line-height:1.8">${d.relatedFactors.map(c => `<li>${c}</li>`).join('')}</ul>` : ''}
        ${d.riskFactors.length ? `<p style="font-weight:600;margin-top:0.75rem">Fatores de Risco:</p><ul style="padding-left:1.5rem;line-height:1.8">${d.riskFactors.map(c => `<li>${c}</li>`).join('')}</ul>` : ''}
        <p style="margin-top:0.75rem;font-size:0.85rem"><span class="tool-category-badge">Evidência: GRADE ${d.evidenceGrade}</span> ${d.sctId ? `· SNOMED CT: ${d.sctId}` : ''}</p>
      </div>
    `;
  }

  function renderNIC() {
    const el = document.getElementById('nicList');
    if (!el) return;
    if (!selectedDx) { el.innerHTML = '<p class="field-hint" style="padding:1rem 0">Selecione um diagnóstico.</p>'; return; }
    const nics = NIC_LINKS[selectedDx.code] || [];
    if (!nics.length) { el.innerHTML = '<p class="field-hint" style="padding:1rem 0">Nenhuma intervenção NIC vinculada.</p>'; return; }
    el.innerHTML = nics.map(n => `
      <div class="nic-item" style="padding:0.75rem;border:1px solid var(--c-border);border-radius:0.5rem;margin-bottom:0.5rem">
        <label style="display:flex;align-items:flex-start;gap:0.5rem;cursor:pointer">
          <input type="checkbox" data-code="${n.code}" data-name="${n.name}" ${selectedNICs.includes(n.code) ? 'checked' : ''} />
          <div>
            <span style="font-weight:600;color:var(--c-primary)">${n.code}</span> — ${n.name}
            <ul style="padding-left:1.5rem;margin-top:0.25rem;line-height:1.6;font-size:0.9rem">${n.activities.map(a => `<li>${a}</li>`).join('')}</ul>
          </div>
        </label>
      </div>
    `).join('');
    el.querySelectorAll('input[type=checkbox]').forEach(cb => {
      cb.addEventListener('change', () => {
        if (cb.checked && !selectedNICs.includes(cb.dataset.code)) selectedNICs.push(cb.dataset.code);
        else selectedNICs = selectedNICs.filter(c => c !== cb.dataset.code);
        updatePlanSummary();
      });
    });
  }

  function renderNOC() {
    const el = document.getElementById('nocList');
    if (!el) return;
    if (!selectedDx) { el.innerHTML = '<p class="field-hint" style="padding:1rem 0">Selecione um diagnóstico.</p>'; return; }
    const nocs = NOC_LINKS[selectedDx.code] || [];
    if (!nocs.length) { el.innerHTML = '<p class="field-hint" style="padding:1rem 0">Nenhum resultado NOC vinculado.</p>'; return; }
    el.innerHTML = nocs.map(n => `
      <div class="noc-item" style="padding:0.75rem;border:1px solid var(--c-border);border-radius:0.5rem;margin-bottom:0.5rem">
        <label style="display:flex;align-items:flex-start;gap:0.5rem;cursor:pointer">
          <input type="checkbox" data-code="${n.code}" data-name="${n.name}" ${selectedNOCs.includes(n.code) ? 'checked' : ''} />
          <div>
            <span style="font-weight:600;color:var(--c-primary)">${n.code}</span> — ${n.name}
            <p style="margin-top:0.25rem;font-size:0.9rem;color:var(--c-text-muted)">Indicadores: ${n.indicators.join(', ')}</p>
          </div>
        </label>
      </div>
    `).join('');
    el.querySelectorAll('input[type=checkbox]').forEach(cb => {
      cb.addEventListener('change', () => {
        if (cb.checked && !selectedNOCs.includes(cb.dataset.code)) selectedNOCs.push(cb.dataset.code);
        else selectedNOCs = selectedNOCs.filter(c => c !== cb.dataset.code);
        updatePlanSummary();
      });
    });
  }

  function updatePlanSummary() {
    const el = document.getElementById('planSummary');
    if (!el) return;
    if (!selectedDx) { el.innerHTML = '<p class="field-hint">Selecione um diagnóstico para começar.</p>'; return; }
    el.innerHTML = `
      <div style="padding:1rem;background:var(--c-surface);border-radius:0.5rem;border:1px solid var(--c-border)">
        <p style="font-weight:600;margin-bottom:0.5rem">Resumo do Plano:</p>
        <p><strong>NANDA:</strong> ${selectedDx.code} — ${selectedDx.name}</p>
        <p><strong>NIC (${selectedNICs.length}):</strong> ${selectedNICs.length ? selectedNICs.join(', ') : 'Nenhuma selecionada'}</p>
        <p><strong>NOC (${selectedNOCs.length}):</strong> ${selectedNOCs.length ? selectedNOCs.join(', ') : 'Nenhum selecionado'}</p>
      </div>
    `;
  }

  function savePlan() {
    if (!selectedDx) { alert('Selecione um diagnóstico primeiro.'); return; }
    const plans = getPlans();
    const plan = {
      id: Date.now().toString(),
      patientName: document.getElementById('planPatient')?.value || '',
      patientAge: document.getElementById('planAge')?.value || '',
      diagnosis: { code: selectedDx.code, name: selectedDx.name },
      interventions: selectedNICs,
      outcomes: selectedNOCs,
      notes: document.getElementById('planNotes')?.value || '',
      status: 'draft',
      createdAt: new Date().toISOString(),
    };
    plans.unshift(plan);
    savePlans(plans);
    renderSavedPlans();
    clearPlan();
  }

  function clearPlan() {
    selectedDx = null;
    selectedNICs = [];
    selectedNOCs = [];
    document.getElementById('planPatient').value = '';
    document.getElementById('planAge').value = '';
    document.getElementById('planNotes').value = '';
    document.getElementById('dxSearch').value = '';
    document.getElementById('dxDomain').value = '';
    renderDxResults('', '');
    renderDxDetail();
    renderNIC();
    renderNOC();
    updatePlanSummary();
  }

  function renderSavedPlans() {
    const el = document.getElementById('savedPlans');
    const statEl = document.getElementById('totalPlansStat');
    if (statEl) statEl.textContent = getPlans().length;
    if (!el) return;
    const plans = getPlans();
    if (!plans.length) { el.innerHTML = '<p class="field-hint" style="padding:1rem 0">Nenhum plano salvo ainda.</p>'; return; }
    el.innerHTML = plans.map(p => `
      <div class="saved-plan-item" style="padding:1rem;border:1px solid var(--c-border);border-radius:0.5rem;margin-bottom:0.75rem">
        <div style="display:flex;justify-content:space-between;align-items:start">
          <div>
            <p style="font-weight:600">${p.diagnosis.code} — ${p.diagnosis.name}</p>
            <p style="font-size:0.85rem;color:var(--c-text-muted)">Paciente: ${p.patientName || 'Não informado'} · Idade: ${p.patientAge || 'N/A'}</p>
            <p style="font-size:0.85rem;color:var(--c-text-muted)">NIC: ${p.interventions.length} · NOC: ${p.outcomes.length}</p>
            <p style="font-size:0.8rem;color:var(--c-text-muted);margin-top:0.25rem">Criado em: ${new Date(p.createdAt).toLocaleDateString('pt-BR')}</p>
          </div>
          <div style="display:flex;gap:0.5rem">
            <span class="tool-category-badge" style="font-size:0.75rem">${p.status}</span>
            <button class="btn-icon" style="font-size:0.8rem;padding:0.25rem 0.5rem" onclick="window.PlanoEnf.deletePlan('${p.id}')">Excluir</button>
          </div>
        </div>
        ${p.notes ? `<p style="margin-top:0.5rem;font-size:0.9rem">${p.notes}</p>` : ''}
      </div>
    `).join('');
  }

  function deletePlan(id) {
    let plans = getPlans();
    plans = plans.filter(p => p.id !== id);
    savePlans(plans);
    renderSavedPlans();
  }

  // ===== Init =====
  function init() {
    const search = document.getElementById('dxSearch');
    const domain = document.getElementById('dxDomain');
    if (search) {
      search.addEventListener('input', () => renderDxResults(search.value, domain.value));
    }
    if (domain) {
      domain.addEventListener('change', () => renderDxResults(search.value, domain.value));
    }
    const saveBtn = document.getElementById('savePlanBtn');
    if (saveBtn) saveBtn.addEventListener('click', savePlan);
    const clearBtn = document.getElementById('clearPlanBtn');
    if (clearBtn) clearBtn.addEventListener('click', clearPlan);

    renderDxResults('', '');
    renderSavedPlans();
  }

  window.PlanoEnf = { deletePlan, init };
  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
