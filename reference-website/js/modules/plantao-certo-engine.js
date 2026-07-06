/**
 * Plantão Certo Engine — Gestão de Escalas
 * Site estático: usa localStorage para persistência
 * Dimensionamento conforme COFEN 543/2017
 */
(function () {
  'use strict';

  const SHIFT_KEY = 'nis_plantao_shifts';
  const LEAVE_KEY = 'nis_plantao_leaves';

  const CARE_HOURS = {
    minimo: 3.0,
    intermediario: 4.0,
    alta: 6.0,
    semi: 8.0,
    intensivo: 17.9,
  };

  const SHIFT_LABELS = {
    manha: 'Manhã',
    tarde: 'Tarde',
    noite: 'Noite',
    '12x36': '12x36',
  };

  const LEAVE_LABELS = {
    ferias: 'Férias',
    licenca: 'Licença',
    maternidade: 'Maternidade',
    medico: 'Afastamento Médico',
  };

  function getShifts() { try { return JSON.parse(localStorage.getItem(SHIFT_KEY) || '[]'); } catch { return []; } }
  function saveShifts(s) { localStorage.setItem(SHIFT_KEY, JSON.stringify(s)); }
  function getLeaves() { try { return JSON.parse(localStorage.getItem(LEAVE_KEY) || '[]'); } catch { return []; } }
  function saveLeaves(l) { localStorage.setItem(LEAVE_KEY, JSON.stringify(l)); }

  function addShift() {
    const unit = val('shiftUnit');
    const name = val('shiftName');
    if (!unit || !name) { alert('Preencha setor e nome.'); return; }
    const shift = {
      id: Date.now().toString(),
      unit, name,
      role: val('shiftRole'),
      shiftType: val('shiftType'),
      date: val('shiftDate'),
      notes: val('shiftNotes'),
      createdAt: new Date().toISOString(),
    };
    const shifts = getShifts();
    shifts.unshift(shift);
    saveShifts(shifts);
    ['shiftUnit', 'shiftName', 'shiftDate', 'shiftNotes'].forEach(clearInput);
    renderShifts();
    renderStats();
  }

  function renderShifts() {
    const el = document.getElementById('shiftList');
    if (!el) return;
    const shifts = getShifts();
    if (!shifts.length) { el.innerHTML = '<p class="field-hint">Nenhum plantão cadastrado.</p>'; return; }
    el.innerHTML = `<table style="width:100%;border-collapse:collapse;font-size:0.9rem">
      <thead><tr style="border-bottom:2px solid var(--c-border)">
        <th style="text-align:left;padding:0.5rem">Setor</th>
        <th style="text-align:left;padding:0.5rem">Profissional</th>
        <th style="text-align:left;padding:0.5rem">Cargo</th>
        <th style="text-align:left;padding:0.5rem">Turno</th>
        <th style="text-align:left;padding:0.5rem">Data</th>
        <th style="text-align:left;padding:0.5rem"></th>
      </tr></thead>
      <tbody>${shifts.map(s => `<tr style="border-bottom:1px solid var(--c-border)">
        <td style="padding:0.5rem">${s.unit}</td>
        <td style="padding:0.5rem">${s.name}</td>
        <td style="padding:0.5rem">${s.role === 'enfermeiro' ? 'Enfermeiro' : 'Técnico'}</td>
        <td style="padding:0.5rem">${SHIFT_LABELS[s.shiftType] || s.shiftType}</td>
        <td style="padding:0.5rem">${s.date ? new Date(s.date).toLocaleDateString('pt-BR') : '—'}</td>
        <td style="padding:0.5rem"><button class="btn-icon" style="font-size:0.8rem;padding:0.25rem 0.5rem" onclick="window.PlantaoCerto.delShift('${s.id}')">Excluir</button></td>
      </tr>`).join('')}</tbody>
    </table>`;
  }

  function delShift(id) {
    saveShifts(getShifts().filter(s => s.id !== id));
    renderShifts();
    renderStats();
  }

  function calcStaffing() {
    const beds = num('dmBeds');
    const occupancy = num('dmOccupancy') / 100;
    const careLevel = val('dmCareLevel');
    if (!beds || !occupancy) { alert('Preencha leitos e taxa de ocupação.'); return; }
    const hoursPerPatient = CARE_HOURS[careLevel] || 4.0;
    const occupiedBeds = Math.round(beds * occupancy);
    const totalHoursDay = occupiedBeds * hoursPerPatient;
    // 42h/semana per professional
    const hoursWeek = totalHoursDay * 7;
    const totalProfessionals = Math.ceil(hoursWeek / 42);
    const nurses = Math.ceil(totalProfessionals * 0.33); // 33% nurses minimum
    const techs = totalProfessionals - nurses;
    const resultEl = document.getElementById('staffingResult');
    if (resultEl) {
      resultEl.innerHTML = `
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem;padding:1rem 0">
          <div style="background:var(--c-surface);border:1px solid var(--c-border);border-radius:0.5rem;padding:1.5rem;text-align:center">
            <p style="font-size:2rem;font-weight:700;color:var(--c-primary)">${occupiedBeds}</p>
            <p class="field-hint">Leitos ocupados</p>
          </div>
          <div style="background:var(--c-surface);border:1px solid var(--c-border);border-radius:0.5rem;padding:1.5rem;text-align:center">
            <p style="font-size:2rem;font-weight:700;color:var(--c-primary)">${hoursPerPatient}h</p>
            <p class="field-hint">Horas/enfermagem</p>
          </div>
          <div style="background:var(--c-surface);border:1px solid var(--c-border);border-radius:0.5rem;padding:1.5rem;text-align:center">
            <p style="font-size:2rem;font-weight:700;color:var(--c-primary)">${totalHoursDay}h</p>
            <p class="field-hint">Horas/dia necessárias</p>
          </div>
          <div style="background:var(--c-surface);border:1px solid var(--c-border);border-radius:0.5rem;padding:1.5rem;text-align:center">
            <p style="font-size:2rem;font-weight:700;color:var(--c-primary)">${totalProfessionals}</p>
            <p class="field-hint">Total profissionais</p>
          </div>
          <div style="background:var(--c-surface);border:1px solid var(--c-border);border-radius:0.5rem;padding:1.5rem;text-align:center">
            <p style="font-size:2rem;font-weight:700;color:var(--c-primary)">${nurses}</p>
            <p class="field-hint">Enfermeiros (≥33%)</p>
          </div>
          <div style="background:var(--c-surface);border:1px solid var(--c-border);border-radius:0.5rem;padding:1.5rem;text-align:center">
            <p style="font-size:2rem;font-weight:700;color:var(--c-primary)">${techs}</p>
            <p class="field-hint">Técnicos</p>
          </div>
        </div>
        <p style="padding:0.5rem 0;font-size:0.9rem;color:var(--c-text-muted)">Base: Resolução COFEN 543/2017. Cálculo: ${occupiedBeds} leitos × ${hoursPerPatient}h = ${totalHoursDay}h/dia × 7 dias = ${hoursWeek}h/semana ÷ 42h/profissional = ${totalProfessionals} profissionais.</p>
      `;
    }
  }

  function addLeave() {
    const name = val('leaveName');
    if (!name) { alert('Preencha o nome.'); return; }
    const start = val('leaveStart');
    const end = val('leaveEnd');
    const days = start && end ? Math.ceil((new Date(end) - new Date(start)) / (1000 * 60 * 60 * 24)) + 1 : 0;
    const leave = {
      id: Date.now().toString(),
      name, type: val('leaveType'),
      start, end, days,
      status: 'pending',
      createdAt: new Date().toISOString(),
    };
    const leaves = getLeaves();
    leaves.unshift(leave);
    saveLeaves(leaves);
    ['leaveName', 'leaveStart', 'leaveEnd'].forEach(clearInput);
    renderLeaves();
    renderStats();
  }

  function renderLeaves() {
    const el = document.getElementById('leaveList');
    if (!el) return;
    const leaves = getLeaves();
    if (!leaves.length) { el.innerHTML = '<p class="field-hint">Nenhuma solicitação registrada.</p>'; return; }
    el.innerHTML = leaves.map(l => `
      <div style="padding:0.75rem;border:1px solid var(--c-border);border-radius:0.5rem;margin-bottom:0.5rem;display:flex;justify-content:space-between;align-items:center">
        <div>
          <p style="font-weight:600">${l.name}</p>
          <p style="font-size:0.85rem;color:var(--c-text-muted)">${LEAVE_LABELS[l.type]} · ${l.start ? new Date(l.start).toLocaleDateString('pt-BR') : '—'} a ${l.end ? new Date(l.end).toLocaleDateString('pt-BR') : '—'} · ${l.days} dias</p>
        </div>
        <div style="display:flex;gap:0.5rem;align-items:center">
          <span class="tool-category-badge" style="font-size:0.75rem">${l.status === 'pending' ? 'Pendente' : l.status === 'approved' ? 'Aprovado' : 'Rejeitado'}</span>
          ${l.status === 'pending' ? `<button class="btn-icon" style="font-size:0.8rem;padding:0.25rem 0.5rem" onclick="window.PlantaoCerto.approveLeave('${l.id}', 'approved')">Aprovar</button><button class="btn-icon" style="font-size:0.8rem;padding:0.25rem 0.5rem" onclick="window.PlantaoCerto.approveLeave('${l.id}', 'rejected')">Rejeitar</button>` : ''}
          <button class="btn-icon" style="font-size:0.8rem;padding:0.25rem 0.5rem" onclick="window.PlantaoCerto.delLeave('${l.id}')">Excluir</button>
        </div>
      </div>
    `).join('');
  }

  function approveLeave(id, status) {
    const leaves = getLeaves();
    const idx = leaves.findIndex(l => l.id === id);
    if (idx >= 0) { leaves[idx].status = status; saveLeaves(leaves); renderLeaves(); }
  }

  function delLeave(id) {
    saveLeaves(getLeaves().filter(l => l.id !== id));
    renderLeaves();
    renderStats();
  }

  function renderStats() {
    const shifts = getShifts();
    const leaves = getLeaves();
    const nurses = shifts.filter(s => s.role === 'enfermeiro').length;
    const techs = shifts.filter(s => s.role === 'tecnico').length;
    setText('statTotalShifts', shifts.length);
    setText('statTotalNurses', nurses);
    setText('statTotalTechs', techs);
    setText('statTotalLeaves', leaves.length);
  }

  // Utils
  function val(id) { return document.getElementById(id)?.value?.trim() || ''; }
  function num(id) { return parseFloat(document.getElementById(id)?.value) || 0; }
  function setText(id, v) { const el = document.getElementById(id); if (el) el.textContent = v; }
  function clearInput(id) { const el = document.getElementById(id); if (el) el.value = ''; }

  function init() {
    document.getElementById('addShiftBtn')?.addEventListener('click', addShift);
    document.getElementById('calcStaffingBtn')?.addEventListener('click', calcStaffing);
    document.getElementById('addLeaveBtn')?.addEventListener('click', addLeave);
    renderShifts();
    renderLeaves();
    renderStats();
  }

  window.PlantaoCerto = { delShift, approveLeave, delLeave, init };
  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
