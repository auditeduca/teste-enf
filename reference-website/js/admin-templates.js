/**
 * NKOS Page Templates — 8 templates completos para criação de novas páginas
 * Cada template gera HTML completo com design system, header/footer, SVG sprite, i18n
 */

window.NKOS_TEMPLATES = {
  "artigo": {
    "name": "Artigo",
    "icon": "fa-newspaper",
    "description": "Artigo educacional sobre tema de enfermagem",
    "fields": [
      {"id": "title", "label": "Título do artigo", "type": "text", "required": true, "placeholder": "Ex: Reanimação Neonatal: Guia Completo"},
      {"id": "category", "label": "Categoria", "type": "select", "options": ["Neonatologia","Emergência","UTI","Geriatria","Saúde Mental","Cardiologia","Pediatria","Obstetrícia","Oncologia","Segurança do Paciente","Cálculo de Medicação","Gestão"]},
      {"id": "author", "label": "Autor", "type": "text", "placeholder": "Ex: Enf. João Silva"},
      {"id": "summary", "label": "Resumo (lead)", "type": "textarea", "placeholder": "Breve resumo do artigo..."},
      {"id": "body", "label": "Corpo do artigo (Markdown)", "type": "richtext", "placeholder": "## Introdução\n\nTexto do artigo..."},
      {"id": "references", "label": "Referências", "type": "textarea", "placeholder": "1. Autor, Título, Ano..."},
      {"id": "tags", "label": "Tags", "type": "text", "placeholder": "#Neonatologia #Reanimação"}
    ],
    "generate": function(data) {
      return NKOS_TEMPLATES._wrap("artigo", data, [
        '<article class="tool-article">',
        '  <header class="tool-article-header">',
        '    <h1>' + (data.title || 'Artigo') + '</h1>',
        '    <p class="tool-article-lead">' + (data.summary || '') + '</p>',
        '    <div class="tool-article-meta"><span>' + (data.author || 'Calculadoras de Enfermagem') + '</span></div>',
        '  </header>',
        '  <div class="tool-article-body">',
        '    ' + NKOS_TEMPLATES._mdToHtml(data.body || ''),
        '  </div>',
        '  ' + (data.references ? '<section class="tool-article-refs"><h3>Referências</h3><p>' + data.references.replace(/\n/g, '<br>') + '</p></section>' : ''),
        '</article>'
      ].join('\n'));
    }
  },

  "protocolo": {
    "name": "Protocolo",
    "icon": "fa-shield-halved",
    "description": "Protocolo institucional de enfermagem",
    "fields": [
      {"id": "title", "label": "Nome do protocolo", "type": "text", "required": true, "placeholder": "Ex: Protocolo de Prevenção de Úlcera por Pressão"},
      {"id": "category", "label": "Categoria", "type": "select", "options": ["Segurança do Paciente","Emergência","UTI","Centro Cirúrgico","Neonatologia","Obstetrícia","Cálculo de Medicação"]},
      {"id": "institution", "label": "Instituição/Órgão", "type": "text", "placeholder": "Ex: ANVISA, OMS, MS"},
      {"id": "objective", "label": "Objetivo", "type": "textarea", "placeholder": "Objetivo do protocolo..."},
      {"id": "steps", "label": "Etapas (uma por linha)", "type": "textarea", "placeholder": "1. Identificar paciente\n2. Avaliar risco\n3. Aplicar intervenções\n4. Monitorar"},
      {"id": "indicators", "label": "Indicadores de qualidade", "type": "textarea", "placeholder": "Taxa de incidência, Taxa de adesão..."},
      {"id": "references", "label": "Referências", "type": "textarea"},
      {"id": "tags", "label": "Tags", "type": "text"}
    ],
    "generate": function(data) {
      var steps = (data.steps || '').split('\n').filter(function(s){return s.trim();});
      var stepsHtml = steps.map(function(s, i) {
        return '<li class="protocolo-step"><span class="step-num">' + (i+1) + '</span><span class="step-text">' + NKOS_TEMPLATES._esc(s) + '</span></li>';
      }).join('\n');
      return NKOS_TEMPLATES._wrap("protocolo", data, [
        '<article class="tool-protocolo">',
        '  <header class="tool-protocolo-header">',
        '    <div class="protocolo-badge"><i class="fa-solid fa-shield-halved"></i> Protocolo</div>',
        '    <h1>' + (data.title || 'Protocolo') + '</h1>',
        '    <p class="tool-protocolo-source">' + (data.institution || '') + '</p>',
        '  </header>',
        '  <section class="tool-protocolo-objective">',
        '    <h3>Objetivo</h3>',
        '    <p>' + NKOS_TEMPLATES._esc(data.objective || '') + '</p>',
        '  </section>',
        '  <section class="tool-protocolo-steps">',
        '    <h3>Etapas</h3>',
        '    <ol class="protocolo-steps-list">' + stepsHtml + '</ol>',
        '  </section>',
        '  ' + (data.indicators ? '<section class="tool-protocolo-indicators"><h3>Indicadores</h3><p>' + NKOS_TEMPLATES._esc(data.indicators) + '</p></section>' : ''),
        '  ' + (data.references ? '<section class="tool-protocolo-refs"><h3>Referências</h3><p>' + data.references.replace(/\n/g,'<br>') + '</p></section>' : ''),
        '</article>'
      ].join('\n'));
    }
  },

  "caso-clinico": {
    "name": "Caso Clínico",
    "icon": "fa-clipboard-list",
    "description": "Caso clínico para ensino e discussão",
    "fields": [
      {"id": "title", "label": "Título do caso", "type": "text", "required": true, "placeholder": "Ex: Paciente com Sepsis em UTI"},
      {"id": "category", "label": "Categoria", "type": "select", "options": ["UTI","Emergência","Cardiologia","Neonatologia","Pediatria","Geriatria","Obstetrícia","Oncologia"]},
      {"id": "patient", "label": "Dados do paciente", "type": "textarea", "placeholder": "Nome, idade, sexo, histórico..."},
      {"id": "complaint", "label": "Queixa principal", "type": "textarea"},
      {"id": "assessment", "label": "Avaliação (sinais vitais, exames)", "type": "textarea"},
      {"id": "diagnosis", "label": "Diagnósticos de enfermagem (NANDA)", "type": "textarea", "placeholder": "NANDA_00046 — Risco de choque..."},
      {"id": "interventions", "label": "Intervenções (NIC)", "type": "textarea"},
      {"id": "outcomes", "label": "Resultados esperados (NOC)", "type": "textarea"},
      {"id": "discussion", "label": "Discussão do caso", "type": "textarea"},
      {"id": "tags", "label": "Tags", "type": "text"}
    ],
    "generate": function(data) {
      return NKOS_TEMPLATES._wrap("caso-clinico", data, [
        '<article class="tool-caso">',
        '  <header class="tool-caso-header">',
        '    <div class="caso-badge"><i class="fa-solid fa-clipboard-list"></i> Caso Clínico</div>',
        '    <h1>' + (data.title || 'Caso Clínico') + '</h1>',
        '  </header>',
        '  <div class="caso-grid">',
        '    <section class="caso-section"><h3><i class="fa-solid fa-user"></i> Paciente</h3><p>' + NKOS_TEMPLATES._esc(data.patient || '') + '</p></section>',
        '    <section class="caso-section"><h3><i class="fa-solid fa-comment-medical"></i> Queixa</h3><p>' + NKOS_TEMPLATES._esc(data.complaint || '') + '</p></section>',
        '    <section class="caso-section"><h3><i class="fa-solid fa-stethoscope"></i> Avaliação</h3><p>' + NKOS_TEMPLATES._esc(data.assessment || '') + '</p></section>',
        '    <section class="caso-section"><h3><i class="fa-solid fa-clipboard-list"></i> Diagnósticos NANDA</h3><p>' + NKOS_TEMPLATES._esc(data.diagnosis || '') + '</p></section>',
        '    <section class="caso-section"><h3><i class="fa-solid fa-hands-holding-medical"></i> Intervenções NIC</h3><p>' + NKOS_TEMPLATES._esc(data.interventions || '') + '</p></section>',
        '    <section class="caso-section"><h3><i class="fa-solid fa-chart-line"></i> Resultados NOC</h3><p>' + NKOS_TEMPLATES._esc(data.outcomes || '') + '</p></section>',
        '  </div>',
        '  <section class="caso-discussion"><h3><i class="fa-solid fa-lightbulb"></i> Discussão</h3><p>' + NKOS_TEMPLATES._esc(data.discussion || '') + '</p></section>',
        '</article>'
      ].join('\n'));
    }
  },

  "checklist": {
    "name": "Check-list",
    "icon": "fa-list-check",
    "description": "Check-list operacional de enfermagem",
    "fields": [
      {"id": "title", "label": "Título do check-list", "type": "text", "required": true, "placeholder": "Ex: Check-list de Segurança Cirúrgica"},
      {"id": "category", "label": "Categoria", "type": "select", "options": ["Centro Cirúrgico","Segurança do Paciente","Emergência","UTI","Neonatologia","Cálculo de Medicação"]},
      {"id": "items", "label": "Itens (um por linha)", "type": "textarea", "required": true, "placeholder": "Confirmar identidade do paciente\nVerificar sítio cirúrgico\nConferir material\nTimeout da equipe"},
      {"id": "tags", "label": "Tags", "type": "text"}
    ],
    "generate": function(data) {
      var items = (data.items || '').split('\n').filter(function(s){return s.trim();});
      var itemsHtml = items.map(function(s) {
        return '<label class="checklist-item"><input type="checkbox"/><span class="checkmark"></span><span class="item-text">' + NKOS_TEMPLATES._esc(s) + '</span></label>';
      }).join('\n');
      return NKOS_TEMPLATES._wrap("checklist", data, [
        '<article class="tool-checklist">',
        '  <header class="tool-checklist-header">',
        '    <div class="checklist-badge"><i class="fa-solid fa-list-check"></i> Check-list</div>',
        '    <h1>' + (data.title || 'Check-list') + '</h1>',
        '  </header>',
        '  <div class="checklist-items">' + itemsHtml + '</div>',
        '  <div class="checklist-progress"><div class="progress-bar" id="clProgress"></div></div>',
        '</article>'
      ].join('\n'));
    }
  },

  "infografico": {
    "name": "Infográfico",
    "icon": "fa-image",
    "description": "Infográfico visual sobre conceito clínico",
    "fields": [
      {"id": "title", "label": "Título", "type": "text", "required": true},
      {"id": "category", "label": "Categoria", "type": "select", "options": ["Neonatologia","Emergência","UTI","Cardiologia","Geriatria","Saúde Mental"]},
      {"id": "sections", "label": "Seções (título: conteúdo, uma por linha)", "type": "textarea", "placeholder": "Definição: Texto explicativo\nCausas: Texto\nTratamento: Texto"},
      {"id": "imageUrl", "label": "URL da imagem (opcional)", "type": "text"},
      {"id": "tags", "label": "Tags", "type": "text"}
    ],
    "generate": function(data) {
      var sections = (data.sections || '').split('\n').filter(function(s){return s.trim();});
      var secHtml = sections.map(function(s) {
        var parts = s.split(':');
        return '<div class="infografico-card"><h4>' + NKOS_TEMPLATES._esc(parts[0] || '') + '</h4><p>' + NKOS_TEMPLATES._esc(parts.slice(1).join(':').trim()) + '</p></div>';
      }).join('\n');
      return NKOS_TEMPLATES._wrap("infografico", data, [
        '<article class="tool-infografico">',
        '  <header class="tool-infografico-header">',
        '    <h1>' + (data.title || 'Infográfico') + '</h1>',
        '  </header>',
        '  ' + (data.imageUrl ? '<div class="infografico-image"><img src="' + NKOS_TEMPLATES._esc(data.imageUrl) + '" alt="' + NKOS_TEMPLATES._esc(data.title) + '" loading="lazy"/></div>' : ''),
        '  <div class="infografico-grid">' + secHtml + '</div>',
        '</article>'
      ].join('\n'));
    }
  },

  "guia-bolso": {
    "name": "Guia de Bolso",
    "icon": "fa-book",
    "description": "Guia de referência rápida",
    "fields": [
      {"id": "title", "label": "Título", "type": "text", "required": true, "placeholder": "Ex: Guia de Bolso — Insulina"},
      {"id": "category", "label": "Categoria", "type": "select", "options": ["Cálculo de Medicação","Emergência","UTI","Neonatologia","Cardiologia"]},
      {"id": "content", "label": "Conteúdo (separar seções com ---)", "type": "textarea", "placeholder": "## Tipos de Insulina\n---\n## Diluição\n---\n## Administração"},
      {"id": "tags", "label": "Tags", "type": "text"}
    ],
    "generate": function(data) {
      var sections = (data.content || '').split('---').filter(function(s){return s.trim();});
      var secHtml = sections.map(function(s) {
        return '<section class="guia-section">' + NKOS_TEMPLATES._mdToHtml(s.trim()) + '</section>';
      }).join('\n');
      return NKOS_TEMPLATES._wrap("guia-bolso", data, [
        '<article class="tool-guia">',
        '  <header class="tool-guia-header">',
        '    <div class="guia-badge"><i class="fa-solid fa-book"></i> Guia de Bolso</div>',
        '    <h1>' + (data.title || 'Guia de Bolso') + '</h1>',
        '  </header>',
        '  <div class="guia-content">' + secHtml + '</div>',
        '</article>'
      ].join('\n'));
    }
  },

  "mapa-mental": {
    "name": "Mapa Mental",
    "icon": "fa-diagram-project",
    "description": "Mapa mental de conceito clínico",
    "fields": [
      {"id": "title", "label": "Título", "type": "text", "required": true},
      {"id": "category", "label": "Categoria", "type": "select", "options": ["Neonatologia","Emergência","UTI","Cardiologia","Geriatria","Saúde Mental","Segurança do Paciente"]},
      {"id": "centerNode", "label": "Nó central", "type": "text", "required": true, "placeholder": "Ex: Sepsis"},
      {"id": "branches", "label": "Ramos (título: sub-itens separados por vírgula)", "type": "textarea", "placeholder": "Definição: resposta inflamatária sistêmica\nSinais: febre, taquicardia, hipotensão\nTratamento: antibiótico, fluidos, vasopressores"},
      {"id": "tags", "label": "Tags", "type": "text"}
    ],
    "generate": function(data) {
      var branches = (data.branches || '').split('\n').filter(function(s){return s.trim();});
      var branchHtml = branches.map(function(b) {
        var parts = b.split(':');
        var title = NKOS_TEMPLATES._esc(parts[0] || '');
        var items = (parts[1] || '').split(',').map(function(i){return '<span class="mapa-leaf">' + NKOS_TEMPLATES._esc(i.trim()) + '</span>';}).join('');
        return '<div class="mapa-branch"><div class="mapa-branch-title">' + title + '</div><div class="mapa-branch-items">' + items + '</div></div>';
      }).join('\n');
      return NKOS_TEMPLATES._wrap("mapa-mental", data, [
        '<article class="tool-mapa-mental">',
        '  <header class="tool-mapa-header">',
        '    <h1>' + (data.title || 'Mapa Mental') + '</h1>',
        '  </header>',
        '  <div class="mapa-container">',
        '    <div class="mapa-center">' + NKOS_TEMPLATES._esc(data.centerNode || 'Conceito') + '</div>',
        '    <div class="mapa-branches">' + branchHtml + '</div>',
        '  </div>',
        '</article>'
      ].join('\n'));
    }
  },

  "slides": {
    "name": "Slides",
    "icon": "fa-display",
    "description": "Apresentação de slides para ensino",
    "fields": [
      {"id": "title", "label": "Título da apresentação", "type": "text", "required": true},
      {"id": "category", "label": "Categoria", "type": "select", "options": ["Neonatologia","Emergência","UTI","Cardiologia","Geriatria","Saúde Mental","Segurança do Paciente","Gestão"]},
      {"id": "slides", "label": "Slides (título: conteúdo, separar slides com ---)", "type": "textarea", "placeholder": "Introdução: Texto do slide 1\n---\nDefinição: Texto do slide 2\n---\nConclusão: Texto final"},
      {"id": "tags", "label": "Tags", "type": "text"}
    ],
    "generate": function(data) {
      var slides = (data.slides || '').split('---').filter(function(s){return s.trim();});
      var slideHtml = slides.map(function(s, i) {
        var parts = s.split(':');
        var title = NKOS_TEMPLATES._esc(parts[0] || ('Slide ' + (i+1)));
        var content = NKOS_TEMPLATES._esc(parts.slice(1).join(':').trim());
        return '<div class="slide" data-slide="' + i + '"><h3>' + title + '</h3><p>' + content + '</p></div>';
      }).join('\n');
      return NKOS_TEMPLATES._wrap("slides", data, [
        '<article class="tool-slides">',
        '  <header class="tool-slides-header">',
        '    <div class="slides-badge"><i class="fa-solid fa-display"></i> Slides</div>',
        '    <h1>' + (data.title || 'Apresentação') + '</h1>',
        '  </header>',
        '  <div class="slides-viewer">' + slideHtml + '</div>',
        '  <div class="slides-controls"><button class="btn-prev">Anterior</button><span class="slide-counter">1/' + slides.length + '</span><button class="btn-next">Próximo</button></div>',
        '</article>'
      ].join('\n'));
    }
  },

  // ─── Helpers ─────────────────────────────────────────────────
  "_mdToHtml": function(md) {
    if (!md) return '';
    var html = md;
    // Headers
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    // Bold/italic
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    // Lists
    html = html.replace(/^\- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.+?<\/li>\n?)+/g, function(m){return '<ul>' + m + '</ul>';});
    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
    // Paragraphs
    html = html.split('\n\n').map(function(p) {
      if (p.startsWith('<')) return p;
      return '<p>' + p.replace(/\n/g, '<br>') + '</p>';
    }).join('\n');
    return html;
  },

  "_esc": function(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  },

  "_wrap": function(type, data, content) {
    var slug = (data.title || type).toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .substring(0, 60);
    var filename = slug + '.html';
    var category = data.category || '';
    var tags = data.tags || '';

    return '<!DOCTYPE html>\n' +
      '<html lang="pt-BR">\n' +
      '<head>\n' +
      '<meta charset="utf-8"/>\n' +
      '<meta content="width=device-width, initial-scale=1.0" name="viewport"/>\n' +
      '<title>' + NKOS_TEMPLATES._esc(data.title || type) + ' — Calculadoras de Enfermagem</title>\n' +
      '<meta name="description" content="' + NKOS_TEMPLATES._esc((data.summary || data.objective || data.title || '').substring(0, 160)) + '"/>\n' +
      '<meta name="robots" content="index,follow"/>\n' +
      '<link rel="canonical" href="https://www.calculadorasdeenfermagem.com.br/' + filename + '"/>\n' +
      '<link rel="preconnect" href="https://www.googletagmanager.com"/>\n' +
      '<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>\n' +
      '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"/>\n' +
      '<link rel="stylesheet" href="site-styles.css"/>\n' +
      '<script type="application/ld+json">\n' +
      '{"@context":"https://schema.org","@type":"Article","name":"' + NKOS_TEMPLATES._esc(data.title || '') + '","inLanguage":"pt-BR","isPartOf":"https://www.calculadorasdeenfermagem.com.br"}</script>\n' +
      '</head>\n' +
      '<body>\n' +
      '<!-- Header -->\n' +
      '<div id="header-placeholder"></div>\n' +
      '<script>fetch("/menu-global.html").then(r=>r.text()).then(h=>document.getElementById("header-placeholder").innerHTML=h);</script>\n' +
      '\n' +
      '<main>\n' +
      '  <div class="container">\n' +
      '    <nav class="tpl-breadcrumb" aria-label="breadcrumb">\n' +
      '      <a href="/index.html">Início</a> > \n' +
      '      <a href="/biblioteca.html">Biblioteca</a> > \n' +
      '      <span>' + NKOS_TEMPLATES._esc(data.title || type) + '</span>\n' +
      '    </nav>\n' +
      '\n' +
      content + '\n' +
      '\n' +
      NKOS_TEMPLATES._footerZone(tags, category) + '\n' +
      '  </div>\n' +
      '</main>\n' +
      '\n' +
      '<!-- Footer -->\n' +
      '<div id="footer-placeholder"></div>\n' +
      '<script>fetch("/menu-global.html").then(r=>r.text()).then(h=>document.getElementById("footer-placeholder").innerHTML=h);</script>\n' +
      '<script src="/js/i18n-loader.js"></script>\n' +
      '</body>\n' +
      '</html>\n';
  },

  "_footerZone": function(tags, category) {
    var tagList = (tags || '').split(/[#,\s]+/).filter(function(t){return t.trim();});
    var tagHtml = tagList.map(function(t) {
      return '<a href="/index.html#calculadoras" class="tool-tag">#' + t + '</a>';
    }).join('\n        ');
    
    // Add standard tags
    tagHtml += '\n        <a href="/diagnosticosnanda.html" class="tool-tag">#NANDA-I</a>';
    tagHtml += '\n        <a href="/sae.html" class="tool-tag">#SAE</a>';
    tagHtml += '\n        <a href="/protocolos.html" class="tool-tag">#Protocolos</a>';
    tagHtml += '\n        <a href="/medicamentos.html" class="tool-tag">#Medicacao</a>';
    tagHtml += '\n        <a href="/simulados.html" class="tool-tag">#Simulados</a>';
    tagHtml += '\n        <a href="/flashcards.html" class="tool-tag">#Flashcards</a>';

    return '    <section class="tool-footer-zone">\n' +
      '      <div class="tool-tags">\n        ' + tagHtml + '\n      </div>\n\n' +
      '      <div class="related-tools">\n' +
      '        <h2 class="related-tools-title">Ferramentas relacionadas</h2>\n' +
      '        <div class="related-tools-grid">\n' +
      '          <a class="related-tool-card" href="/biblioteca.html"><div class="related-icon-wrap"><svg class="icon"><use href="#i-book"/></svg></div><div><h3>Biblioteca</h3><p>Recursos</p></div></a>\n' +
      '          <a class="related-tool-card" href="/simulados.html"><div class="related-icon-wrap"><svg class="icon"><use href="#i-clipboard"/></svg></div><div><h3>Simulados</h3><p>Simulação</p></div></a>\n' +
      '          <a class="related-tool-card" href="/sae.html"><div class="related-icon-wrap"><svg class="icon"><use href="#i-clipboard"/></svg></div><div><h3>SAE</h3><p>Sistematização</p></div></a>\n' +
      '          <a class="related-tool-card" href="/diagnosticosnanda.html"><div class="related-icon-wrap"><svg class="icon"><use href="#i-clipboard-list"/></svg></div><div><h3>NANDA-I</h3><p>Diagnósticos</p></div></a>\n' +
      '          <a class="related-tool-card" href="/protocolos.html"><div class="related-icon-wrap"><svg class="icon"><use href="#i-shield"/></svg></div><div><h3>Protocolos</h3><p>Protocolos</p></div></a>\n' +
      '          <a class="related-tool-card" href="/flashcards.html"><div class="related-icon-wrap"><svg class="icon"><use href="#i-clipboard"/></svg></div><div><h3>Flashcards</h3><p>Estudo</p></div></a>\n' +
      '        </div>\n      </div>\n    </section>';
  }
};
