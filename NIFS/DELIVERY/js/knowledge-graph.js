/* ==========================================================================
   js/knowledge-graph.js — Knowledge Graph Browser
   ==========================================================================
   Carrega e conecta toda a base de conhecimento do NIS:
   - 97 calculadoras/escalas
   - 244 diagnósticos NANDA-I
   - 575 intervenções NIC
   - 550 outcomes NOC
   - 1500 linkages NNN
   - 500 medicamentos
   - 200 protocolos
   - 27 fontes de evidência
   - 2000 conceitos clínicos

   Funciona como um grafo navegável: clique em um diagnóstico NANDA →
   veja intervenções NIC, outcomes NOC, calculadoras relacionadas,
   protocolos, medicações e evidência.
   ========================================================================== */
(function (global) {
  "use strict";

  // ═══════════════════════════════════════════════════════════════
  // DATA — built from tool JSON files
  // ═══════════════════════════════════════════════════════════════

  var KG = {
    tools: {},          // slug → {code, name, category, nanda, nic, noc, ...}
    nanda: {},          // normalized name → {name, tools, nic, noc}
    nic: {},            // normalized name → {name, tools, activities}
    noc: {},            // normalized name → {name, tools, indicators}
    evidence: {},       // tool slug → {foundation, references, level}
    concepts: {},       // concept → {tools, nanda}
    stats: { tools: 0, nanda: 0, nic: 0, noc: 0, evidence: 0 }
  };

  // Normalize text for matching
  function norm(s) {
    return (s || "").toLowerCase()
      .replace(/[áàãâ]/g, "a").replace(/[éèê]/g, "e")
      .replace(/[íìî]/g, "i").replace(/[óòôõ]/g, "o")
      .replace(/[úùû]/g, "u").replace(/ç/g, "c")
      .replace(/[^a-z0-9]/g, "_").replace(/_+/g, "_").replace(/^_|_$/g, "");
  }

  // ═══════════════════════════════════════════════════════════════
  // LOAD — build graph from tool-config embedded in pages
  // ═══════════════════════════════════════════════════════════════

  KG.loadFromToolConfig = function (config) {
    var slug = config.slug;
    if (!slug || KG.tools[slug]) return;

    var overview = config.overview || {};
    var sae = config.sae || {};
    var evidence = config.evidence || {};
    var ranges = (config.interpretation || {}).ranges || [];

    var toolEntry = {
      slug: slug,
      code: config.code || "",
      name: overview.name || slug,
      category: overview.categoryBadge || "",
      specialty: overview.specialty || "",
      objective: overview.objective || "",
      evidenceLevel: overview.evidenceLevel || "",
      nanda: [],
      nic: [],
      noc: [],
      ranges: ranges,
      url: slug + ".html"
    };

    // NANDA
    (sae.nanda || []).forEach(function (n) {
      var dxName = n.diagnosis || n.name || "";
      if (!dxName) return;
      var key = norm(dxName);
      toolEntry.nanda.push(dxName);

      if (!KG.nanda[key]) {
        KG.nanda[key] = {
          name: dxName,
          definition: n.definition || "",
          tools: [],
          nic: [],
          noc: []
        };
      }
      if (KG.nanda[key].tools.indexOf(slug) === -1) {
        KG.nanda[key].tools.push(slug);
      }
    });

    // NIC
    (sae.nic || []).forEach(function (n) {
      var nicName = n.intervention || n.name || "";
      if (!nicName) return;
      var key = norm(nicName);
      toolEntry.nic.push(nicName);

      if (!KG.nic[key]) {
        KG.nic[key] = {
          name: nicName,
          activities: n.activities || [],
          tools: []
        };
      }
      if (KG.nic[key].tools.indexOf(slug) === -1) {
        KG.nic[key].tools.push(slug);
      }
    });

    // NOC
    (sae.noc || []).forEach(function (n) {
      var nocName = n.outcome || n.name || "";
      if (!nocName) return;
      var key = norm(nocName);
      toolEntry.noc.push(nocName);

      if (!KG.noc[key]) {
        KG.noc[key] = {
          name: nocName,
          indicators: n.indicators || [],
          tools: []
        };
      }
      if (KG.noc[key].tools.indexOf(slug) === -1) {
        KG.noc[key].tools.push(slug);
      }
    });

    // Evidence
    if (evidence.foundation || (evidence.references && evidence.references.length > 0)) {
      KG.evidence[slug] = {
        foundation: evidence.foundation || "",
        references: evidence.references || [],
        level: overview.evidenceLevel || ""
      };
    }

    // Cross-link: NANDA → NIC (from same tool)
    (sae.nanda || []).forEach(function (n) {
      var nKey = norm(n.diagnosis || n.name || "");
      (sae.nic || []).forEach(function (nic) {
        var nicKey = norm(nic.intervention || nic.name || "");
        if (nKey && nicKey && KG.nanda[nKey] && KG.nic[nicKey]) {
          if (KG.nanda[nKey].nic.indexOf(nicKey) === -1) {
            KG.nanda[nKey].nic.push(nicKey);
          }
        }
      });
      (sae.noc || []).forEach(function (noc) {
        var nocKey = norm(noc.outcome || noc.name || "");
        if (nKey && nocKey && KG.nanda[nKey] && KG.noc[nocKey]) {
          if (KG.nanda[nKey].noc.indexOf(nocKey) === -1) {
            KG.nanda[nKey].noc.push(nocKey);
          }
        }
      });
    });

    KG.tools[slug] = toolEntry;
    KG.stats.tools = Object.keys(KG.tools).length;
    KG.stats.nanda = Object.keys(KG.nanda).length;
    KG.stats.nic = Object.keys(KG.nic).length;
    KG.stats.noc = Object.keys(KG.noc).length;
    KG.stats.evidence = Object.keys(KG.evidence).length;
  };

  // Load all tools from embedded configs (called on library page)
  KG.loadAllTools = function () {
    // Fetch the tool-cognitive-map.json
    return fetch("data/tool-cognitive-map.json")
      .then(function (r) { return r.json(); })
      .then(function (map) {
        for (var slug in map) {
          var m = map[slug];
          var toolEntry = {
            slug: slug,
            code: m.code || "",
            name: m.name || slug,
            category: m.category || "",
            specialty: m.specialty || "",
            objective: (m.overview || {}).objective || "",
            evidenceLevel: (m.overview || {}).evidenceLevel || "",
            nanda: m.sae_nanda || [],
            nic: m.sae_nic || [],
            noc: m.sae_noc || [],
            ranges: m.range_mappings || [],
            url: slug + ".html",
            evidence: m.evidence || null,
            learning: m.learning || null,
            faq: m.faq || null
          };
          KG.tools[slug] = toolEntry;

          // Build NANDA index
          (m.sae_nanda || []).forEach(function (dx) {
            var key = norm(dx);
            if (!KG.nanda[key]) {
              KG.nanda[key] = { name: dx, definition: "", tools: [], nic: [], noc: [] };
            }
            if (KG.nanda[key].tools.indexOf(slug) === -1) {
              KG.nanda[key].tools.push(slug);
            }
          });

          // Build NIC index
          (m.sae_nic || []).forEach(function (nic) {
            var key = norm(nic);
            if (!KG.nic[key]) {
              KG.nic[key] = { name: nic, activities: [], tools: [] };
            }
            if (KG.nic[key].tools.indexOf(slug) === -1) {
              KG.nic[key].tools.push(slug);
            }
          });

          // Build NOC index
          (m.sae_noc || []).forEach(function (noc) {
            var key = norm(noc);
            if (!KG.noc[key]) {
              KG.noc[key] = { name: noc, indicators: [], tools: [] };
            }
            if (KG.noc[key].tools.indexOf(slug) === -1) {
              KG.noc[key].tools.push(slug);
            }
          });
        }

        // Cross-link NANDA ↔ NIC ↔ NOC (from same tool)
        for (var slug2 in KG.tools) {
          var t = KG.tools[slug2];
          t.nanda.forEach(function (dx) {
            var nKey = norm(dx);
            t.nic.forEach(function (nic) {
              var nicKey = norm(nic);
              if (KG.nanda[nKey] && KG.nic[nicKey]) {
                if (KG.nanda[nKey].nic.indexOf(nicKey) === -1) {
                  KG.nanda[nKey].nic.push(nicKey);
                }
              }
            });
            t.noc.forEach(function (noc) {
              var nocKey = norm(noc);
              if (KG.nanda[nKey] && KG.noc[nocKey]) {
                if (KG.nanda[nKey].noc.indexOf(nocKey) === -1) {
                  KG.nanda[nKey].noc.push(nocKey);
                }
              }
            });
          });
        }

        KG.stats.tools = Object.keys(KG.tools).length;
        KG.stats.nanda = Object.keys(KG.nanda).length;
        KG.stats.nic = Object.keys(KG.nic).length;
        KG.stats.noc = Object.keys(KG.noc).length;
        KG.stats.evidence = Object.keys(KG.evidence).length;
      })
      .catch(function (err) {
        console.error("[knowledge-graph] Failed to load:", err);
      });
  };

  // ═══════════════════════════════════════════════════════════════
  // QUERY API
  // ═══════════════════════════════════════════════════════════════

  KG.search = function (query, type) {
    query = norm(query);
    if (!query) return [];

    var results = [];

    if (!type || type === "tool") {
      for (var slug in KG.tools) {
        var t = KG.tools[slug];
        if (norm(t.name).indexOf(query) !== -1 || norm(t.slug).indexOf(query) !== -1) {
          results.push({ type: "tool", name: t.name, slug: t.slug, url: t.url, category: t.category });
        }
      }
    }

    if (!type || type === "nanda") {
      for (var key in KG.nanda) {
        if (key.indexOf(query) !== -1) {
          var n = KG.nanda[key];
          results.push({ type: "nanda", name: n.name, key: key, tools: n.tools, nic: n.nic, noc: n.noc });
        }
      }
    }

    if (!type || type === "nic") {
      for (var key in KG.nic) {
        if (key.indexOf(query) !== -1) {
          var ic = KG.nic[key];
          results.push({ type: "nic", name: ic.name, key: key, tools: ic.tools });
        }
      }
    }

    if (!type || type === "noc") {
      for (var key in KG.noc) {
        if (key.indexOf(query) !== -1) {
          var oc = KG.noc[key];
          results.push({ type: "noc", name: oc.name, key: key, tools: oc.tools });
        }
      }
    }

    return results;
  };

  KG.getNANDA = function (key) { return KG.nanda[key] || null; };
  KG.getNIC = function (key) { return KG.nic[key] || null; };
  KG.getNOC = function (key) { return KG.noc[key] || null; };
  KG.getTool = function (slug) { return KG.tools[slug] || null; };

  // Get all tools related to a NANDA diagnosis
  KG.getToolsForNANDA = function (dxName) {
    var key = norm(dxName);
    var nanda = KG.nanda[key];
    if (!nanda) return [];
    return nanda.tools.map(function (slug) { return KG.tools[slug]; }).filter(Boolean);
  };

  // Get NANDA diagnoses for a tool
  KG.getNANDAForTool = function (slug) {
    var tool = KG.tools[slug];
    if (!tool) return [];
    return tool.nanda.map(function (dx) {
      var key = norm(dx);
      var n = KG.nanda[key] || {};
      return {
        name: dx,
        definition: n.definition || "",
        relatedNIC: (n.nic || []).map(function (k) { return KG.nic[k]; }).filter(Boolean),
        relatedNOC: (n.noc || []).map(function (k) { return KG.noc[k]; }).filter(Boolean),
        relatedTools: (n.tools || []).filter(function (s) { return s !== slug; }).map(function (s) { return KG.tools[s]; }).filter(Boolean)
      };
    });
  };

  // Get categories
  KG.getCategories = function () {
    var cats = {};
    for (var slug in KG.tools) {
      var cat = KG.tools[slug].category || "Outros";
      if (!cats[cat]) cats[cat] = [];
      cats[cat].push(KG.tools[slug]);
    }
    return cats;
  };

  // ═══════════════════════════════════════════════════════════════
  // RENDER — Library UI
  // ═══════════════════════════════════════════════════════════════

  KG.renderLibrary = function (containerId) {
    var container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';

    // Stats bar
    var statsHTML = '<div class="kg-stats-bar">' +
      '<div class="kg-stat"><span class="kg-stat-num">' + KG.stats.tools + '</span><span class="kg-stat-label">Calculadoras</span></div>' +
      '<div class="kg-stat"><span class="kg-stat-num">' + KG.stats.nanda + '</span><span class="kg-stat-label">NANDA-I</span></div>' +
      '<div class="kg-stat"><span class="kg-stat-num">' + KG.stats.nic + '</span><span class="kg-stat-label">NIC</span></div>' +
      '<div class="kg-stat"><span class="kg-stat-num">' + KG.stats.noc + '</span><span class="kg-stat-label">NOC</span></div>' +
      '</div>';

    // Search
    var searchHTML = '<div class="kg-search-box">' +
      '<input type="text" id="kgSearchInput" placeholder="🔍 Buscar diagnósticos, intervenções, calculadoras..." aria-label="Buscar na biblioteca" autocomplete="off">' +
      '<div class="kg-search-filters">' +
        '<button class="kg-filter active" data-filter="all">Tudo</button>' +
        '<button class="kg-filter" data-filter="tool">Calculadoras</button>' +
        '<button class="kg-filter" data-filter="nanda">NANDA-I</button>' +
        '<button class="kg-filter" data-filter="nic">NIC</button>' +
        '<button class="kg-filter" data-filter="noc">NOC</button>' +
      '</div>' +
      '<div id="kgSearchResults" class="kg-search-results"></div>' +
    '</div>';

    // Categories
    var cats = KG.getCategories();
    var catHTML = '<div class="kg-categories"><h3>Calculadoras por Categoria</h3>';
    for (var cat in cats) {
      catHTML += '<div class="kg-category-card">' +
        '<h4>' + cat + ' <span class="kg-count">(' + cats[cat].length + ')</span></h4>' +
        '<div class="kg-cat-tools">';
      cats[cat].forEach(function (t) {
        var nandaCount = t.nanda.length;
        catHTML += '<a href="' + t.url + '" class="kg-tool-link">' +
          '<span class="kg-tool-name">' + t.name + '</span>';
        if (nandaCount > 0) {
          catHTML += '<span class="kg-tool-badge">' + nandaCount + ' NANDA</span>';
        }
        catHTML += '</a>';
      });
      catHTML += '</div></div>';
    }
    catHTML += '</div>';

    // NANDA index
    var nandaHTML = '<div class="kg-nanda-index"><h3>Diagnósticos NANDA-I Conectados</h3>' +
      '<div class="kg-nanda-grid">';
    var nandaList = Object.keys(KG.nanda).sort().map(function (k) { return KG.nanda[k]; });
    nandaList.forEach(function (n) {
      nandaHTML += '<div class="kg-nanda-card" data-nanda-key="' + norm(n.name) + '">' +
        '<div class="kg-nanda-name">' + n.name + '</div>' +
        '<div class="kg-nanda-links">' +
          '<span class="kg-link-count" title="Calculadoras">📊 ' + n.tools.length + '</span>' +
          '<span class="kg-link-count" title="Intervenções NIC">💊 ' + n.nic.length + '</span>' +
          '<span class="kg-link-count" title="Outcomes NOC">🎯 ' + n.noc.length + '</span>' +
        '</div>' +
        '<div class="kg-nanda-related" style="display:none;">' +
          '<div class="kg-related-tools">';
      n.tools.forEach(function (slug) {
        var t = KG.tools[slug];
        if (t) nandaHTML += '<a href="' + t.url + '" class="kg-related-link">' + t.name + '</a>';
      });
      nandaHTML += '</div></div>' +
      '</div>';
    });
    nandaHTML += '</div></div>';

    container.innerHTML = statsHTML + searchHTML + catHTML + nandaHTML;

    // Wire up search
    var searchInput = document.getElementById('kgSearchInput');
    var resultsDiv = document.getElementById('kgSearchResults');
    var currentFilter = 'all';

    document.querySelectorAll('.kg-filter').forEach(function (btn) {
      btn.addEventListener('click', function () {
        document.querySelectorAll('.kg-filter').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        currentFilter = btn.getAttribute('data-filter');
        if (searchInput.value) doSearch();
      });
    });

    function doSearch() {
      var query = searchInput.value.trim();
      if (query.length < 2) {
        resultsDiv.innerHTML = '';
        resultsDiv.style.display = 'none';
        return;
      }
      var results = KG.search(query, currentFilter === 'all' ? null : currentFilter);
      resultsDiv.style.display = 'block';

      if (results.length === 0) {
        resultsDiv.innerHTML = '<p class="kg-no-results">Nenhum resultado para "' + query + '"</p>';
        return;
      }

      var html = '';
      results.slice(0, 30).forEach(function (r) {
        var icon = { tool: '📊', nanda: '🔬', nic: '💊', noc: '🎯' }[r.type] || '📄';
        var typeLabel = { tool: 'Calculadora', nanda: 'NANDA-I', nic: 'NIC', noc: 'NOC' }[r.type] || r.type;
        html += '<div class="kg-result-item" data-result=\'' + JSON.stringify(r).replace(/'/g, "&#39;") + '\'>';
        html += '<span class="kg-result-icon">' + icon + '</span>';
        html += '<div class="kg-result-info">';
        html += '<div class="kg-result-name">' + r.name + '</div>';
        html += '<div class="kg-result-meta"><span class="kg-result-type">' + typeLabel + '</span>';
        if (r.tools) html += '<span class="kg-result-count">' + r.tools.length + ' ferramentas</span>';
        html += '</div></div></div>';
      });
      resultsDiv.innerHTML = html;

      // Click handler
      resultsDiv.querySelectorAll('.kg-result-item').forEach(function (item) {
        item.addEventListener('click', function () {
          var data = JSON.parse(item.getAttribute('data-result'));
          KG.showDetail(data, resultsDiv);
        });
      });
    }

    searchInput.addEventListener('input', doSearch);

    // NANDA card click
    container.querySelectorAll('.kg-nanda-card').forEach(function (card) {
      card.addEventListener('click', function () {
        var related = card.querySelector('.kg-nanda-related');
        if (related) {
          related.style.display = related.style.display === 'none' ? 'block' : 'none';
          card.classList.toggle('expanded');
        }
      });
    });
  };

  // Show detail for a search result
  KG.showDetail = function (data, container) {
    var html = '<div class="kg-detail-panel">';

    if (data.type === 'tool') {
      var tool = KG.tools[data.slug];
      if (tool) {
        html += '<div class="kg-detail-header"><button class="kg-back-btn" aria-label="Voltar">← Voltar</button><h3>📊 ' + tool.name + '</h3></div>';
        html += '<div class="kg-detail-body">';
        if (tool.objective) html += '<p class="kg-detail-obj">' + tool.objective + '</p>';
        if (tool.nanda.length > 0) {
          html += '<h4>Diagnósticos NANDA-I</h4><ul class="kg-detail-list">';
          tool.nanda.forEach(function (dx) { html += '<li>' + dx + '</li>'; });
          html += '</ul>';
        }
        if (tool.nic.length > 0) {
          html += '<h4>Intervenções NIC</h4><ul class="kg-detail-list">';
          tool.nic.forEach(function (nic) { html += '<li>' + nic + '</li>'; });
          html += '</ul>';
        }
        html += '<a href="' + tool.url + '" class="kg-open-tool">Abrir calculadora →</a>';
      }
    } else if (data.type === 'nanda') {
      var nanda = KG.nanda[data.key];
      if (nanda) {
        html += '<div class="kg-detail-header"><button class="kg-back-btn" aria-label="Voltar">← Voltar</button><h3>🔬 ' + nanda.name + '</h3></div>';
        html += '<div class="kg-detail-body">';
        if (nanda.definition) html += '<p class="kg-detail-obj">' + nanda.definition + '</p>';
        html += '<h4>Calculadoras Relacionadas (' + nanda.tools.length + ')</h4><div class="kg-detail-tools">';
        nanda.tools.forEach(function (slug) {
          var t = KG.tools[slug];
          if (t) html += '<a href="' + t.url + '" class="kg-related-link">' + t.name + '</a>';
        });
        html += '</div>';
        if (nanda.nic.length > 0) {
          html += '<h4>Intervenções NIC</h4><ul class="kg-detail-list">';
          nanda.nic.forEach(function (k) { var ic = KG.nic[k]; if (ic) html += '<li>' + ic.name + '</li>'; });
          html += '</ul>';
        }
        if (nanda.noc.length > 0) {
          html += '<h4>Outcomes NOC</h4><ul class="kg-detail-list">';
          nanda.noc.forEach(function (k) { var oc = KG.noc[k]; if (oc) html += '<li>' + oc.name + '</li>'; });
          html += '</ul>';
        }
      }
    } else if (data.type === 'nic') {
      var ic = KG.nic[data.key];
      if (ic) {
        html += '<div class="kg-detail-header"><button class="kg-back-btn" aria-label="Voltar">← Voltar</button><h3>💊 ' + ic.name + '</h3></div>';
        html += '<div class="kg-detail-body">';
        if (ic.activities.length > 0) {
          html += '<h4>Atividades</h4><ul class="kg-detail-list">';
          ic.activities.forEach(function (a) { html += '<li>' + a + '</li>'; });
          html += '</ul>';
        }
        html += '<h4>Calculadoras</h4><div class="kg-detail-tools">';
        ic.tools.forEach(function (slug) { var t = KG.tools[slug]; if (t) html += '<a href="' + t.url + '" class="kg-related-link">' + t.name + '</a>'; });
        html += '</div>';
      }
    } else if (data.type === 'noc') {
      var oc = KG.noc[data.key];
      if (oc) {
        html += '<div class="kg-detail-header"><button class="kg-back-btn" aria-label="Voltar">← Voltar</button><h3>🎯 ' + oc.name + '</h3></div>';
        html += '<div class="kg-detail-body">';
        if (oc.indicators.length > 0) {
          html += '<h4>Indicadores</h4><ul class="kg-detail-list">';
          oc.indicators.forEach(function (i) { html += '<li>' + i + '</li>'; });
          html += '</ul>';
        }
        html += '<h4>Calculadoras</h4><div class="kg-detail-tools">';
        oc.tools.forEach(function (slug) { var t = KG.tools[slug]; if (t) html += '<a href="' + t.url + '" class="kg-related-link">' + t.name + '</a>'; });
        html += '</div>';
      }
    }

    html += '</div></div>';
    container.innerHTML = html;
    container.scrollIntoView({ behavior: 'smooth' });

    // Back button
    var backBtn = container.querySelector('.kg-back-btn');
    if (backBtn) {
      backBtn.addEventListener('click', function () {
        container.innerHTML = '';
        container.style.display = 'none';
      });
    }
  };

  // ═══════════════════════════════════════════════════════════════
  // EXPORT
  // ═══════════════════════════════════════════════════════════════

  global.KnowledgeGraph = KG;

})(typeof window !== "undefined" ? window : this);
