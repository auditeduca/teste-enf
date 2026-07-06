/**
 * EnfermaCV Engine — Construtor de Currículos
 * Site estático: wizard multi-step + localStorage
 */
(function () {
  'use strict';
  const STORAGE_KEY = 'nis_enfermacv_cvs';
  let currentStep = 1;
  const experiences = [];
  const educations = [];

  function getCvs() { try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); } catch { return []; } }
  function saveCvs(c) { localStorage.setItem(STORAGE_KEY, JSON.stringify(c)); }

  function showStep(n) {
    currentStep = n;
    document.querySelectorAll('.cv-step').forEach(s => s.style.display = s.dataset.stepContent === String(n) ? '' : 'none');
    document.querySelectorAll('.step-dot').forEach(d => {
      const active = parseInt(d.dataset.step) === n;
      d.style.background = active ? 'var(--c-primary)' : 'var(--c-surface)';
      d.style.color = active ? '#fff' : 'var(--c-text-muted)';
      d.style.border = active ? 'none' : '1px solid var(--c-border)';
    });
    if (n === 5) updatePreview();
  }

  function addExp() {
    const exp = { inst: val('expInst'), role: val('expRole'), start: val('expStart'), end: val('expEnd'), desc: val('expDesc') };
    if (!exp.inst || !exp.role) { alert('Preencha instituição e cargo.'); return; }
    experiences.push(exp);
    ['expInst', 'expRole', 'expStart', 'expEnd', 'expDesc'].forEach(clearInput);
    renderExpList();
    updatePreview();
  }

  function renderExpList() {
    const el = document.getElementById('cvExpList');
    if (!el) return;
    if (!experiences.length) { el.innerHTML = ''; return; }
    el.innerHTML = experiences.map((e, i) => `
      <div style="padding:0.5rem;border:1px solid var(--c-border);border-radius:0.5rem;margin-bottom:0.5rem">
        <strong>${e.role}</strong> — ${e.inst}
        <span style="font-size:0.8rem;color:var(--c-text-muted)"> (${e.start || ''} - ${e.end || 'atual'})</span>
        <button class="btn-icon" style="font-size:0.75rem;padding:0.2rem 0.4rem;margin-left:0.5rem" onclick="window.EnfermaCV.delExp(${i})">Remover</button>
      </div>`).join('');
  }

  function delExp(i) { experiences.splice(i, 1); renderExpList(); updatePreview(); }

  function addEdu() {
    const edu = { inst: val('eduInst'), degree: val('eduDegree'), field: val('eduField'), start: val('eduStart'), end: val('eduEnd') };
    if (!edu.inst) { alert('Preencha a instituição.'); return; }
    educations.push(edu);
    ['eduInst', 'eduField', 'eduStart', 'eduEnd'].forEach(clearInput);
    renderEduList();
    updatePreview();
  }

  function renderEduList() {
    const el = document.getElementById('cvEduList');
    if (!el) return;
    if (!educations.length) { el.innerHTML = ''; return; }
    el.innerHTML = educations.map((e, i) => `
      <div style="padding:0.5rem;border:1px solid var(--c-border);border-radius:0.5rem;margin-bottom:0.5rem">
        <strong>${e.degree}</strong> — ${e.field}
        <span style="font-size:0.8rem;color:var(--c-text-muted)"> (${e.start || ''} - ${e.end || ''})</span>
        <button class="btn-icon" style="font-size:0.75rem;padding:0.2rem 0.4rem;margin-left:0.5rem" onclick="window.EnfermaCV.delEdu(${i})">Remover</button>
      </div>`).join('');
  }

  function delEdu(i) { educations.splice(i, 1); renderEduList(); updatePreview(); }

  function updatePreview() {
    const name = val('cvName') || 'Seu Nome';
    const title = val('cvTitle') || 'Título Profissional';
    const email = val('cvEmail');
    const phone = val('cvPhone');
    const city = val('cvCity');
    const coren = val('cvCoren');
    const summary = val('cvSummary');
    const skills = val('cvSkills')?.split(',').map(s => s.trim()).filter(Boolean) || [];
    const certs = val('cvCerts')?.split(',').map(s => s.trim()).filter(Boolean) || [];
    const langs = val('cvLangs')?.split(',').map(s => s.trim()).filter(Boolean) || [];
    const template = val('cvTemplate') || 'classic';

    const contactLine = [email, phone, city, coren].filter(Boolean).join(' · ');
    const el = document.getElementById('cvPreview');
    if (!el) return;

    const styleMap = {
      classic: 'border-left:4px solid var(--c-primary)',
      modern: 'border-top:4px solid var(--c-primary)',
      minimal: 'border:1px solid var(--c-border)',
    };

    el.innerHTML = `
      <div style="padding:1.5rem;${styleMap[template] || styleMap.classic}">
        <h1 style="font-size:1.5rem;font-weight:800;color:var(--c-primary);margin-bottom:0.25rem">${name}</h1>
        <p style="font-size:1.1rem;color:var(--c-text-muted);margin-bottom:0.5rem">${title}</p>
        ${contactLine ? `<p style="font-size:0.85rem;color:var(--c-text-muted);margin-bottom:1rem">${contactLine}</p>` : ''}
        ${summary ? `<h2 style="font-size:1rem;font-weight:700;border-bottom:1px solid var(--c-border);padding-bottom:0.25rem;margin-bottom:0.5rem">Resumo</h2><p style="font-size:0.9rem;line-height:1.6;margin-bottom:1rem">${summary}</p>` : ''}
        ${experiences.length ? `<h2 style="font-size:1rem;font-weight:700;border-bottom:1px solid var(--c-border);padding-bottom:0.25rem;margin-bottom:0.5rem">Experiência Profissional</h2>${experiences.map(e => `<div style="margin-bottom:0.75rem"><p style="font-weight:600">${e.role}</p><p style="font-size:0.85rem;color:var(--c-text-muted)">${e.inst} · ${e.start || ''} — ${e.end || 'atual'}</p>${e.desc ? `<p style="font-size:0.85rem;line-height:1.5">${e.desc}</p>` : ''}</div>`).join('')}` : ''}
        ${educations.length ? `<h2 style="font-size:1rem;font-weight:700;border-bottom:1px solid var(--c-border);padding-bottom:0.25rem;margin-bottom:0.5rem;margin-top:1rem">Formação Acadêmica</h2>${educations.map(e => `<div style="margin-bottom:0.5rem"><p style="font-weight:600">${e.degree} — ${e.field}</p><p style="font-size:0.85rem;color:var(--c-text-muted)">${e.inst} · ${e.start || ''} — ${e.end || ''}</p></div>`).join('')}` : ''}
        ${skills.length ? `<h2 style="font-size:1rem;font-weight:700;border-bottom:1px solid var(--c-border);padding-bottom:0.25rem;margin-bottom:0.5rem;margin-top:1rem">Competências</h2><p style="font-size:0.9rem">${skills.join(' · ')}</p>` : ''}
        ${certs.length ? `<h2 style="font-size:1rem;font-weight:700;border-bottom:1px solid var(--c-border);padding-bottom:0.25rem;margin-bottom:0.5rem;margin-top:1rem">Certificações</h2><p style="font-size:0.9rem">${certs.join(' · ')}</p>` : ''}
        ${langs.length ? `<h2 style="font-size:1rem;font-weight:700;border-bottom:1px solid var(--c-border);padding-bottom:0.25rem;margin-bottom:0.5rem;margin-top:1rem">Idiomas</h2><p style="font-size:0.9rem">${langs.join(' · ')}</p>` : ''}
      </div>
    `;
  }

  function saveCv() {
    const cv = {
      id: Date.now().toString(),
      name: val('cvName'),
      title: val('cvTitle'),
      email: val('cvEmail'),
      phone: val('cvPhone'),
      city: val('cvCity'),
      coren: val('cvCoren'),
      summary: val('cvSummary'),
      experiences: [...experiences],
      educations: [...educations],
      skills: val('cvSkills')?.split(',').map(s => s.trim()).filter(Boolean) || [],
      certs: val('cvCerts')?.split(',').map(s => s.trim()).filter(Boolean) || [],
      langs: val('cvLangs')?.split(',').map(s => s.trim()).filter(Boolean) || [],
      template: val('cvTemplate') || 'classic',
      createdAt: new Date().toISOString(),
    };
    if (!cv.name) { alert('Preencha pelo menos o nome.'); return; }
    const cvs = getCvs();
    cvs.unshift(cv);
    saveCvs(cvs);
    renderSavedCvs();
    alert('Currículo salvo!');
  }

  function renderSavedCvs() {
    const el = document.getElementById('savedCvs');
    if (!el) return;
    const cvs = getCvs();
    if (!cvs.length) { el.innerHTML = '<p class="field-hint">Nenhum currículo salvo ainda.</p>'; return; }
    el.innerHTML = cvs.map(c => `
      <div style="padding:0.75rem;border:1px solid var(--c-border);border-radius:0.5rem;margin-bottom:0.5rem;display:flex;justify-content:space-between;align-items:center">
        <div>
          <p style="font-weight:600">${c.name}</p>
          <p style="font-size:0.85rem;color:var(--c-text-muted)">${c.title || 'Sem título'} · ${c.template} · ${new Date(c.createdAt).toLocaleDateString('pt-BR')}</p>
        </div>
        <div style="display:flex;gap:0.5rem">
          <button class="btn-icon" style="font-size:0.8rem;padding:0.25rem 0.5rem" onclick="window.EnfermaCV.printCv('${c.id}')">Ver</button>
          <button class="btn-icon" style="font-size:0.8rem;padding:0.25rem 0.5rem" onclick="window.EnfermaCV.delCv('${c.id}')">Excluir</button>
        </div>
      </div>
    `).join('');
  }

  function printCv(id) {
    const cv = getCvs().find(c => c.id === id);
    if (!cv) return;
    const w = window.open('', '_blank');
    w.document.write(`<html><head><title>${cv.name} — Currículo</title><style>body{font-family:Manrope,sans-serif;max-width:800px;margin:0 auto;padding:2rem;color:#1a1a1a}h1{color:#1a3e74}h2{border-bottom:1px solid #ccc;padding-bottom:0.25rem}</style></head><body>
      <h1>${cv.name}</h1><p style="font-size:1.1rem;color:#666">${cv.title || ''}</p>
      <p style="font-size:0.85rem;color:#666">${[cv.email, cv.phone, cv.city, cv.coren].filter(Boolean).join(' · ')}</p>
      ${cv.summary ? `<h2>Resumo</h2><p>${cv.summary}</p>` : ''}
      ${cv.experiences?.length ? `<h2>Experiência</h2>${cv.experiences.map(e => `<div><strong>${e.role}</strong> — ${e.inst} (${e.start || ''} — ${e.end || 'atual'})<br><span style="font-size:0.9rem">${e.desc || ''}</span></div>`).join('<br>')}` : ''}
      ${cv.educations?.length ? `<h2>Formação</h2>${cv.educations.map(e => `<div><strong>${e.degree} — ${e.field}</strong><br>${e.inst} (${e.start || ''} — ${e.end || ''})</div>`).join('<br>')}` : ''}
      ${cv.skills?.length ? `<h2>Competências</h2><p>${cv.skills.join(' · ')}</p>` : ''}
      ${cv.certs?.length ? `<h2>Certificações</h2><p>${cv.certs.join(' · ')}</p>` : ''}
      ${cv.langs?.length ? `<h2>Idiomas</h2><p>${cv.langs.join(' · ')}</p>` : ''}
      <script>window.print()<\/script></body></html>`);
    w.document.close();
  }

  function delCv(id) { saveCvs(getCvs().filter(c => c.id !== id)); renderSavedCvs(); }

  function val(id) { return document.getElementById(id)?.value?.trim() || ''; }
  function clearInput(id) { const el = document.getElementById(id); if (el) el.value = ''; }

  function init() {
    document.getElementById('cvNext1')?.addEventListener('click', () => { updatePreview(); showStep(2); });
    document.getElementById('cvNext2')?.addEventListener('click', () => { updatePreview(); showStep(3); });
    document.getElementById('cvNext3')?.addEventListener('click', () => { updatePreview(); showStep(4); });
    document.getElementById('cvNext4')?.addEventListener('click', () => { updatePreview(); showStep(5); });
    document.getElementById('cvBack2')?.addEventListener('click', () => showStep(1));
    document.getElementById('cvBack3')?.addEventListener('click', () => showStep(2));
    document.getElementById('cvBack4')?.addEventListener('click', () => showStep(3));
    document.getElementById('cvBack5')?.addEventListener('click', () => showStep(4));
    document.getElementById('addExpBtn')?.addEventListener('click', addExp);
    document.getElementById('addEduBtn')?.addEventListener('click', addEdu);
    document.getElementById('cvSaveBtn')?.addEventListener('click', saveCv);
    document.getElementById('cvPrintBtn')?.addEventListener('click', () => window.print());
    ['cvName', 'cvTitle', 'cvEmail', 'cvPhone', 'cvCity', 'cvCoren', 'cvSummary', 'cvSkills', 'cvCerts', 'cvLangs'].forEach(id => {
      document.getElementById(id)?.addEventListener('input', updatePreview);
    });
    renderSavedCvs();
  }

  window.EnfermaCV = { delExp, delEdu, printCv, delCv, init };
  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
