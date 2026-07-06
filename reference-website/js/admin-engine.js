/**
 * NKOS Admin Engine v2.0 — Painel completo de gestão do website
 * Gerencia: páginas, grafo clínico, conteúdo, templates, trilhas, publicação
 */

(function(){
'use strict';

var ADMIN_KEY = 'nkos_admin_session';
var PASSWORD_KEY = 'nkos_admin_password';
var CONTENT_KEY = 'nkos_admin_content';
var DEFAULT_PASSWORD = 'nkos2026';

var currentTemplate = 'artigo';
var currentPageFilter = 'all';

// ─── Auth ─────────────────────────────────────────────────────────
window.adminLogin = function(){
  var input = document.getElementById('adminPassword').value;
  var stored = localStorage.getItem(PASSWORD_KEY) || DEFAULT_PASSWORD;
  if(input === stored){
    sessionStorage.setItem(ADMIN_KEY, 'true');
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('adminLayout').style.display = 'flex';
    initAdmin();
    toast('Bem-vindo, Leivis!');
  } else {
    document.getElementById('loginError').style.display = 'block';
    document.getElementById('adminPassword').value = '';
  }
};

window.adminLogout = function(){
  sessionStorage.removeItem(ADMIN_KEY);
  document.getElementById('adminLayout').style.display = 'none';
  document.getElementById('loginScreen').style.display = 'flex';
  document.getElementById('adminPassword').value = '';
};

if(sessionStorage.getItem(ADMIN_KEY) === 'true'){
  document.getElementById('loginScreen').style.display = 'none';
  document.getElementById('adminLayout').style.display = 'flex';
  initAdmin();
}

// ─── Init ─────────────────────────────────────────────────────────

// ═══ NKOS Admin API Client ═══
const ADMIN_API_URL = '/api/functions/adminApi';

async function adminApi(action, data = {}) {
  try {
    const response = await fetch(ADMIN_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, ...data }),
    });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return await response.json();
  } catch (err) {
    console.warn('Admin API fallback to localStorage:', err);
    return null;
  }
}

// Cache for API data
let _dashboardCache = null;
let _trilhasCache = null;


function initAdmin(){
  populateDropdowns();
  renderDashboard();
  renderPages();
  renderTrilhas();
  renderGrafo();
  renderTemplates();
  renderContentList();
}

function populateDropdowns(){
  var inv = window.NKOS_INVENTORY || {pages: []};
  var calcs = inv.pages.filter(function(p){return p.type === 'calculator';});

  var conceptSel = document.getElementById('contentConcept');
  if(conceptSel){
    calcs.forEach(function(c){
      var opt = document.createElement('option');
      opt.value = c.file;
      opt.textContent = c.title;
      conceptSel.appendChild(opt);
    });
  }

  var specSel = document.getElementById('contentSpecialty');
  if(specSel && window.COFEN_581_2018){
    Object.keys(window.COFEN_581_2018.areas).forEach(function(areaKey){
      var area = window.COFEN_581_2018.areas[areaKey];
      var og = document.createElement('optgroup');
      og.label = 'Área ' + areaKey + ' — ' + area.titulo.substring(0,40) + '...';
      area.especialidades.forEach(function(esp){
        var opt = document.createElement('option');
        opt.value = esp.id;
        opt.textContent = esp.nome;
        og.appendChild(opt);
      });
      specSel.appendChild(og);
    });
  }

  var grafoSel = document.getElementById('grafoCenter');
  if(grafoSel){
    calcs.forEach(function(c){
      var opt = document.createElement('option');
      opt.value = c.file;
      opt.textContent = c.title;
      grafoSel.appendChild(opt);
    });
  }
}

// ─── View Switching ───────────────────────────────────────────────
window.switchView = function(view){
  document.querySelectorAll('.admin-view').forEach(function(v){ v.classList.remove('active'); });
  document.querySelectorAll('.admin-nav-item').forEach(function(n){ n.classList.remove('active'); });
  var viewEl = document.getElementById('view-' + view);
  if(viewEl) viewEl.classList.add('active');
  var navEl = document.querySelector('.admin-nav-item[data-view="' + view + '"]');
  if(navEl) navEl.classList.add('active');
  var titles = {
    'dashboard': 'Dashboard', 'pages': 'Páginas do Site', 'editor': 'Editor de Conteúdo',
    'templates': 'Criar Nova Página', 'trilhas': 'Trilhas COFEN 581/2018',
    'grafo': 'Grafo Clínico', 'publicar': 'Publicar via GitHub',
    'social': 'Redes Sociais', 'config': 'Configurações'
  };
  document.getElementById('viewTitle').textContent = titles[view] || 'Dashboard';
  if(window.innerWidth <= 768) document.getElementById('adminSidebar').classList.remove('open');
};

window.toggleSidebar = function(){
  document.getElementById('adminSidebar').classList.toggle('open');
};

// ─── Dashboard ────────────────────────────────────────────────────
async function renderDashboard() {
    const data = await adminApi('dashboard');
    if (data && data.success) {
      const d = data.dashboard;
      document.getElementById('view-dashboard').innerHTML = `
        <div class="dashboard-grid">
          <div class="stat-card">
            <div class="stat-number">${d.total_content}</div>
            <div class="stat-label">Conteúdos</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">${d.total_trails}</div>
            <div class="stat-label">Trilhas COFEN</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">${d.total_pages}</div>
            <div class="stat-label">Páginas</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">${d.areas.area_1}</div>
            <div class="stat-label">Área I</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">${d.areas.area_2}</div>
            <div class="stat-label">Área II</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">${d.areas.area_3}</div>
            <div class="stat-label">Área III</div>
          </div>
        </div>
      `;
      return;
    }
    // Fallback to original dashboard
    document.getElementById('view-dashboard').innerHTML = '<p class="muted">Conectando ao backend...</p>';
  }

// ─── Pages View ───────────────────────────────────────────────────
function renderPages(){
  var container = document.getElementById('pagesContainer');
  if(!container) return;
  var inv = window.NKOS_INVENTORY || {pages: []};

  // Filter buttons
  var types = ['all', 'calculator', 'tool', 'educational', 'template', 'career', 'wellness', 'institutional', 'home', 'other'];
  var typeLabels = {
    'all': 'Todas', 'calculator': 'Calculadoras', 'tool': 'Ferramentas',
    'educational': 'Educativo', 'template': 'Templates', 'career': 'Carreiras',
    'wellness': 'Bem-estar', 'institutional': 'Institucional', 'home': 'Home', 'other': 'Outros'
  };

  var filterHtml = '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px">';
  types.forEach(function(t){
    var count = t === 'all' ? inv.pages.length : inv.pages.filter(function(p){return p.type === t;}).length;
    filterHtml += '<button class="filter-pill' + (t === 'all' ? ' active' : '') + '" data-filter="' + t + '" onclick="filterPages(\'' + t + '\')">' + typeLabels[t] + ' (' + count + ')</button>';
  });
  filterHtml += '</div>';

  // Search
  filterHtml += '<div style="margin-bottom:16px"><input type="text" id="pageSearch" placeholder="Buscar página..." oninput="searchPages()" style="width:100%;padding:10px 14px;border:1px solid var(--line);border-radius:8px;font-size:14px"/></div>';

  // Table
  filterHtml += '<div id="pagesTable"></div>';
  container.innerHTML = filterHtml;
  renderPagesTable(inv.pages);
}

window.filterPages = function(type){
  currentPageFilter = type;
  document.querySelectorAll('.filter-pill').forEach(function(b){ b.classList.remove('active'); });
  document.querySelector('.filter-pill[data-filter="' + type + '"]').classList.add('active');
  var inv = window.NKOS_INVENTORY || {pages: []};
  var filtered = type === 'all' ? inv.pages : inv.pages.filter(function(p){return p.type === type;});
  renderPagesTable(filtered);
};

window.searchPages = function(){
  var q = (document.getElementById('pageSearch').value || '').toLowerCase();
  var inv = window.NKOS_INVENTORY || {pages: []};
  var filtered = inv.pages.filter(function(p){
    if(currentPageFilter !== 'all' && p.type !== currentPageFilter) return false;
    return p.file.toLowerCase().indexOf(q) !== -1 || p.title.toLowerCase().indexOf(q) !== -1;
  });
  renderPagesTable(filtered);
};

function renderPagesTable(pages){
  var table = document.getElementById('pagesTable');
  if(!table) return;
  if(!pages.length){
    table.innerHTML = '<p style="text-align:center;color:var(--muted);padding:20px">Nenhuma página encontrada.</p>';
    return;
  }
  table.innerHTML = '<table class="admin-table"><thead><tr><th>Arquivo</th><th>Título</th><th>Tipo</th><th>Categoria</th><th>Ações</th></tr></thead><tbody>' +
    pages.map(function(p){
      return '<tr><td><code>' + p.file + '</code></td><td>' + esc(p.title.substring(0,40)) + '</td><td><span class="type-badge type-' + p.type + '">' + p.type + '</span></td><td>' + esc(p.category) + '</td>' +
        '<td class="action-btns"><button onclick="previewPage(\'' + p.file + '\')"><i class="fa-solid fa-eye"></i></button><button onclick="editPageMeta(\'' + p.file + '\')"><i class="fa-solid fa-pen"></i></button></td></tr>';
    }).join('') + '</tbody></table>';
}

window.previewPage = function(file){
  window.open(file, '_blank');
};

window.editPageMeta = function(file){
  toast('Edição de metadados: ' + file);
  // In production, this would open a meta editor
};

// ─── Templates View (Create New Page) ─────────────────────────────
function renderTemplates(){
  var container = document.getElementById('templatesContainer');
  if(!container || !window.NKOS_TEMPLATES) return;

  var templates = window.NKOS_TEMPLATES;
  var tplKeys = ['artigo','protocolo','caso-clinico','checklist','infografico','guia-bolso','mapa-mental','slides'];

  // Template picker
  var pickerHtml = '<div class="template-picker" style="grid-template-columns:repeat(4,1fr);margin-bottom:24px">';
  tplKeys.forEach(function(key){
    var tpl = templates[key];
    pickerHtml += '<div class="template-card' + (key === currentTemplate ? ' active' : '') + '" data-template="' + key + '" onclick="selectTemplate(\'' + key + '\')">' +
      '<i class="fa-solid ' + tpl.icon + '"></i><span>' + tpl.name + '</span></div>';
  });
  pickerHtml += '</div>';

  // Form fields
  var formHtml = '<div id="templateForm"></div>';
  container.innerHTML = pickerHtml + formHtml;
  renderTemplateForm();
}

window.selectTemplate = function(template){
  currentTemplate = template;
  document.querySelectorAll('.template-card').forEach(function(c){ c.classList.remove('active'); });
  document.querySelector('.template-card[data-template="' + template + '"]').classList.add('active');
  renderTemplateForm();
};

function renderTemplateForm(){
  var container = document.getElementById('templateForm');
  if(!container || !window.NKOS_TEMPLATES) return;
  var tpl = window.NKOS_TEMPLATES[currentTemplate];
  if(!tpl) return;

  var html = '<div class="admin-panel"><div class="admin-panel-header"><div><h2>' + tpl.name + '</h2><p>' + tpl.description + '</p></div>' +
    '<div style="display:flex;gap:8px"><button class="btn-action btn-outline" onclick="previewGenerated()"><i class="fa-solid fa-eye"></i> Preview</button>' +
    '<button class="btn-action" onclick="generatePage()"><i class="fa-solid fa-file-code"></i> Gerar Página</button></div></div>';

  html += '<div class="editor-grid"><div class="editor-main">';
  tpl.fields.forEach(function(field){
    html += '<div class="editor-field"><label>' + field.label;
    if(field.required) html += ' <span style="color:#dc2626">*</span>';
    html += '</label>';
    if(field.type === 'select') {
      html += '<select id="fld_' + field.id + '" style="width:100%;padding:10px 14px;border:1px solid var(--line);border-radius:8px;font-size:14px">';
      html += '<option value="">Selecione...</option>';
      field.options.forEach(function(opt){
        html += '<option value="' + opt + '">' + opt + '</option>';
      });
      html += '</select>';
    } else if(field.type === 'textarea' || field.type === 'richtext') {
      html += '<textarea id="fld_' + field.id + '" placeholder="' + (field.placeholder || '') + '" style="width:100%;padding:10px 14px;border:1px solid var(--line);border-radius:8px;font-size:14px;min-height:160px;resize:vertical;font-family:inherit"></textarea>';
    } else {
      html += '<input type="text" id="fld_' + field.id + '" placeholder="' + (field.placeholder || '') + '" style="width:100%;padding:10px 14px;border:1px solid var(--line);border-radius:8px;font-size:14px"/>';
    }
    html += '</div>';
  });
  html += '</div>';

  // Sidebar with preview
  html += '<div class="editor-sidebar"><h3 style="font-family:Sora;font-size:14px;font-weight:700;margin-bottom:16px">Preview</h3>' +
    '<div id="livePreview" style="background:var(--blue-50);border-radius:8px;padding:16px;font-size:12px;min-height:200px;max-height:400px;overflow-y:auto">Preencha os campos para ver o preview...</div>' +
    '<div style="margin-top:16px;padding:12px;background:var(--blue-50);border-radius:8px;font-size:12px;color:var(--muted)"><i class="fa-solid fa-circle-info"></i> A página gerada inclui header, footer, breadcrumb, SVG sprite, i18n, SEO meta tags, JSON-LD e tool-footer-zone com hashtags e ferramentas relacionadas.</div>' +
    '</div></div></div>';

  container.innerHTML = html;

  // Add live preview listeners
  tpl.fields.forEach(function(field){
    var el = document.getElementById('fld_' + field.id);
    if(el) el.addEventListener('input', updateLivePreview);
  });
}

function updateLivePreview(){
  var tpl = window.NKOS_TEMPLATES[currentTemplate];
  if(!tpl) return;
  var data = {};
  tpl.fields.forEach(function(field){
    var el = document.getElementById('fld_' + field.id);
    if(el) data[field.id] = el.value;
  });
  var preview = document.getElementById('livePreview');
  if(preview){
    var html = tpl.generate(data);
    // Strip to body content only for preview
    var bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/);
    var body = bodyMatch ? bodyMatch[1] : html;
    // Remove scripts
    body = body.replace(/<script[^>]*>[\s\S]*?<\/script>/g, '');
    body = body.replace(/<div id="header-placeholder">[\s\S]*?<\/div>/g, '');
    body = body.replace(/<div id="footer-placeholder">[\s\S]*?<\/div>/g, '');
    preview.innerHTML = body;
  }
}

window.previewGenerated = function(){
  updateLivePreview();
  toast('Preview atualizado');
};

window.generatePage = function(){
  var tpl = window.NKOS_TEMPLATES[currentTemplate];
  if(!tpl) return;

  var data = {};
  var required = [];
  tpl.fields.forEach(function(field){
    var el = document.getElementById('fld_' + field.id);
    if(el) data[field.id] = el.value;
    if(field.required && !el.value.trim()) required.push(field.label);
  });

  if(required.length > 0){
    toast('Campos obrigatórios: ' + required.join(', '), true);
    return;
  }

  var html = tpl.generate(data);

  // Generate filename
  var slug = (data.title || currentTemplate).toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .substring(0, 60);
  var filename = slug + '.html';

  // Save to content store
  var content = getContent();
  var id = 'c_' + Date.now();
  content.push({
    id: id, template: currentTemplate, title: data.title || currentTemplate,
    filename: filename, html: html, status: 'draft',
    date: new Date().toISOString().split('T')[0],
    data: data
  });
  localStorage.setItem(CONTENT_KEY, JSON.stringify(content));

  // Download the file
  var blob = new Blob([html], {type: 'text/html'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();

  toast('Página gerada: ' + filename);
  renderDashboard();
  renderContentList();
};

// ─── Content List ─────────────────────────────────────────────────
async function renderContentList(type) {
    const data = await adminApi('content', { type });
    if (data && data.success) {
      const html = (data.items || []).map(item => `
        <div class="content-item" data-id="${item.id}">
          <h4>${item.title}</h4>
          <span class="badge ${item.status}">${item.status}</span>
          <span class="badge">${item.content_type}</span>
        </div>
      `).join('');
      const container = document.getElementById('view-editor') || document.getElementById('contentList');
      if (container) container.innerHTML = html || '<p class="muted">Nenhum conteúdo cadastrado.</p>';
      return;
    }
  }

window.downloadContent = function(id){
  var content = getContent();
  var item = content.find(function(c){return c.id === id;});
  if(!item || !item.html) { toast('Conteúdo sem HTML', true); return; }
  var blob = new Blob([item.html], {type: 'text/html'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = item.filename || (item.id + '.html');
  a.click();
  toast('Download: ' + (item.filename || item.id));
};

window.deleteContent = function(id){
  var content = getContent().filter(function(c){return c.id !== id;});
  localStorage.setItem(CONTENT_KEY, JSON.stringify(content));
  toast('Conteúdo excluído');
  renderContentList();
  renderDashboard();
};

window.editContent = function(id){
  var content = getContent();
  var item = content.find(function(c){return c.id === id;});
  if(!item) return;
  switchView('templates');
  if(item.template) selectTemplate(item.template);
  // Fill fields
  if(item.data){
    Object.keys(item.data).forEach(function(key){
      var el = document.getElementById('fld_' + key);
      if(el) el.value = item.data[key] || '';
    });
  }
  toast('Editando: ' + item.title);
};

function getContent(){
  try { return JSON.parse(localStorage.getItem(CONTENT_KEY) || '[]'); }
  catch(e) { return []; }
}

function getTemplateIcon(tpl){
  var icons = {
    'artigo': 'fa-newspaper', 'protocolo': 'fa-shield-halved', 'caso-clinico': 'fa-clipboard-list',
    'checklist': 'fa-list-check', 'infografico': 'fa-image', 'guia-bolso': 'fa-book',
    'mapa-mental': 'fa-diagram-project', 'slides': 'fa-display',
  };
  return icons[tpl] || 'fa-file';
}

// ─── Trilhas ──────────────────────────────────────────────────────
async function renderTrilhas() {
    const data = await adminApi('trilhas');
    if (data && data.success && data.items.length > 0) {
      const html = data.items.map(t => `
        <div class="trilha-card" data-area="${t.area}">
          <h3>${t.name}</h3>
          <p class="muted">${t.description}</p>
          <div class="trilha-steps">
            ${(t.steps || []).map(s => `<span class="step-badge">${s.order}. ${s.title}</span>`).join('')}
          </div>
          <div class="trilha-meta">
            <span class="badge">${t.cofen_resolution}</span>
            <span class="badge badge-area">${t.area}</span>
          </div>
        </div>
      `).join('');
      document.getElementById('view-trilhas').innerHTML = html;
      return;
    }
    // Fallback to COFEN_581_2018 local data
    if (window.COFEN_581_2018) {
      const trilhas = window.COFEN_581_2018.trilhas || {};
      const areas = window.COFEN_581_2018.areas || {};
      let html = '';
      for (const [espId, trilha] of Object.entries(trilhas)) {
        const esp = Object.values(areas).flatMap(a => a.especialidades || []).find(e => e.id === espId);
        html += `<div class="trilha-card"><h3>${esp ? esp.nome : espId}</h3><p>${trilha.calculadoras?.length || 0} calculadoras, ${trilha.recursos?.length || 0} recursos</p></div>`;
      }
      document.getElementById('view-trilhas').innerHTML = html;
    }
  }

window.showTrilhaDetail = function(espId){
  var data = window.COFEN_581_2018;
  var trilha = data.trilhas[espId];
  if(!trilha){ toast('Trilha pendente', true); return; }
  var name = '';
  Object.keys(data.areas).forEach(function(k){
    data.areas[k].especialidades.forEach(function(e){ if(e.id === espId) name = e.nome; });
  });
  var html = '<div style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.5);z-index:999;display:flex;align-items:center;justify-content:center;padding:20px" onclick="this.remove()">' +
    '<div style="background:#fff;border-radius:16px;padding:32px;max-width:600px;width:100%;max-height:80vh;overflow-y:auto" onclick="event.stopPropagation()">' +
    '<h2 style="font-family:Sora;font-size:20px;font-weight:800;margin-bottom:8px">' + name + '</h2>' +
    '<p style="color:var(--muted);font-size:14px;margin-bottom:20px">' + trilha.desc + '</p>' +
    '<h3 style="font-size:14px;font-weight:700;margin-bottom:10px">Calculadoras (' + trilha.calculadoras.length + ')</h3>' +
    '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px">' +
      trilha.calculadoras.map(function(c){return '<a href="' + c + '" target="_blank" class="tool-tag" style="text-decoration:none">' + c.replace('.html','') + '</a>';}).join('') + '</div>' +
    '<h3 style="font-size:14px;font-weight:700;margin-bottom:10px">Recursos (' + trilha.recursos.length + ')</h3>' +
    '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px">' +
      trilha.recursos.map(function(r){return '<a href="' + r + '" target="_blank" class="tool-tag" style="text-decoration:none">' + r.replace('.html','') + '</a>';}).join('') + '</div>' +
    (trilha.diagnosticos.length ? '<h3 style="font-size:14px;font-weight:700;margin-bottom:10px">NANDA (' + trilha.diagnosticos.length + ')</h3><div style="display:flex;flex-wrap:wrap;gap:6px">' +
      trilha.diagnosticos.map(function(d){return '<span class="tool-tag">' + d + '</span>';}).join('') + '</div>' : '') +
    '</div></div>';
  document.body.insertAdjacentHTML('beforeend', html);
};

window.exportTrilhas = function(){
  if(!window.COFEN_581_2018) return;
  var blob = new Blob([JSON.stringify(window.COFEN_581_2018, null, 2)], {type: 'application/json'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'cofen-581-trilhas.json';
  a.click();
  toast('Trilhas exportadas!');
};

// ─── Grafo ────────────────────────────────────────────────────────
window.renderGrafo = function(){
  var canvas = document.getElementById('grafoCanvas');
  if(!canvas) return;
  var center = document.getElementById('grafoCenter') ? document.getElementById('grafoCenter').value : 'apgar.html';
  var centerName = center.replace('.html','').replace(/-/g,' ');

  var related = [];
  if(window.COFEN_581_2018){
    Object.keys(window.COFEN_581_2018.trilhas).forEach(function(espId){
      var trilha = window.COFEN_581_2018.trilhas[espId];
      if(trilha.calculadoras.indexOf(center) !== -1){
        Object.keys(window.COFEN_581_2018.areas).forEach(function(k){
          window.COFEN_581_2018.areas[k].especialidades.forEach(function(e){
            if(e.id === espId) related.push({type:'specialty', name:e.nome, ref:espId});
          });
        });
        trilha.calculadoras.forEach(function(c){
          if(c !== center) related.push({type:'calculator', name:c.replace('.html','').replace(/-/g,' '), ref:c});
        });
      }
    });
  }
  ['sae.html','sbar.html','simulados.html','flashcards.html','diagnosticosnanda.html','protocolos.html'].forEach(function(g){
    related.push({type:'resource', name:g.replace('.html','').replace(/-/g,' '), ref:g});
  });

  var html = '';
  var centerX = 50, centerY = 50;
  html += '<div class="grafo-node central" style="left:' + centerX + '%;top:' + centerY + '%;transform:translate(-50%,-50%)">' + centerName + '</div>';

  var radius = 35;
  var maxNodes = Math.min(related.length, 12);
  for(var i = 0; i < maxNodes; i++){
    var angle = (i / maxNodes) * Math.PI * 2 - Math.PI / 2;
    var x = centerX + Math.cos(angle) * radius;
    var y = centerY + Math.sin(angle) * radius;
    var node = related[i];
    var nodeClass = 'grafo-node' + (node.type === 'specialty' ? ' central' : '');
    var dx = (x - centerX), dy = (y - centerY);
    var dist = Math.sqrt(dx*dx + dy*dy);
    var edgeAngle = Math.atan2(dy, dx) * 180 / Math.PI;
    html += '<div class="grafo-edge" style="left:' + centerX + '%;top:' + centerY + '%;width:' + dist + '%;transform:rotate(' + edgeAngle + 'deg)"></div>';
    html += '<div class="' + nodeClass + '" style="left:' + x + '%;top:' + y + '%;transform:translate(-50%,-50%)" onclick="window.location.href=\'' + node.ref + '\'">' + node.name + '</div>';
  }
  canvas.innerHTML = html;
};

// ─── Publish ──────────────────────────────────────────────────────
window.publishToGitHub = function(){
  var content = getContent();
  var published = content.filter(function(c){return c.status === 'published';});
  if(published.length === 0){ toast('Nenhum conteúdo publicado', true); return; }
  document.getElementById('modifiedFiles').innerHTML = '<strong>' + published.length + ' arquivos</strong> prontos:<br>' +
    published.map(function(c){return '<code>' + (c.filename || c.id) + '</code>';}).join('<br>');
  toast('Publicação: ' + published.length + ' arquivos');
};

window.generateSocialCard = function(){
  var source = document.getElementById('socialSource');
  if(!source || !source.value){ toast('Selecione uma fonte', true); return; }
  toast('Card gerado para: ' + source.value.replace('.html',''));
};

window.generateLinkedInPost = function(){
  var content = getContent();
  if(content.length === 0){ toast('Crie conteúdo primeiro', true); return; }
  var latest = content[content.length - 1];
  var post = latest.title + '\n\n' + (latest.data && latest.data.summary ? latest.data.summary : '') + '\n\n' +
    'calculadorasdeenfermagem.com.br\n#Enfermagem #Saude #Calculadoras';
  navigator.clipboard.writeText(post).then(function(){ toast('Post copiado!'); }).catch(function(){ toast('Post gerado (console)'); console.log(post); });
};

// ─── Config ───────────────────────────────────────────────────────
window.changePassword = function(){
  var newPass = document.getElementById('configPassword').value;
  if(newPass.length < 4){ toast('Senha muito curta', true); return; }
  localStorage.setItem(PASSWORD_KEY, newPass);
  document.getElementById('configPassword').value = '';
  toast('Senha alterada!');
};

// ─── Utils ────────────────────────────────────────────────────────
function esc(str){
  var div = document.createElement('div');
  div.textContent = str || '';
  return div.innerHTML;
}

function toast(msg, isError){
  var t = document.getElementById('adminToast');
  t.textContent = msg;
  t.style.background = isError ? '#dc2626' : 'var(--blue-600)';
  t.classList.add('show');
  setTimeout(function(){ t.classList.remove('show'); }, 3000);
}

window.toast = toast;
})();
