/**
 * CKO-CART-001 — cart renderer + conference tool + export
 */
(function () {
  "use strict";

  var STORAGE_KEY = "cko-cart-001:conference";
  var NAVY = "#1A3E74";
  var state = {
    manifest: null,
    activeZone: null,
    conference: null,
    timestamp: null
  };

  /** Resolve site-root paths so fetch works under http.server and nested pages. */
  function siteUrl(absPath) {
    var path = String(absPath || "").replace(/^\//, "");
    try {
      var base = document.querySelector("base");
      if (base && base.href) return new URL(path, base.href).href;
      var parts = window.location.pathname.replace(/\\/g, "/").split("/").filter(Boolean);
      if (parts.length && /\.[a-z0-9]+$/i.test(parts[parts.length - 1])) parts.pop();
      var prefix = parts.map(function () { return ".."; }).join("/");
      return (prefix ? prefix + "/" : "") + path;
    } catch (e) {
      return "/" + path;
    }
  }

  var MANIFEST_URL = siteUrl("/data/cko-cart-001.manifest.json");

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  function $all(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function escapeHtml(str) {
    return String(str == null ? "" : str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function announce(msg) {
    var live = $("#cart-live");
    if (live) live.textContent = msg;
  }

  function daysUntil(dateStr) {
    if (!dateStr) return null;
    var d = new Date(dateStr + "T00:00:00");
    if (isNaN(d.getTime())) return null;
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    return Math.round((d - today) / 86400000);
  }

  function addDaysISO(days) {
    var d = new Date();
    d.setDate(d.getDate() + days);
    return d.toISOString().slice(0, 10);
  }

  function statusLabel(status, rules) {
    var map = (rules && rules.statuses) || {};
    return map[status] || status;
  }

  function evaluateItem(itemDef, row, rules) {
    if (!row.present) {
      return {
        status: "critico",
        reasons: [rules.rules.find(function (r) { return r.id === "rule-absent"; }).message]
      };
    }
    var reasons = [];
    var status = "conforme";
    if (itemDef.tracksSeal && rules.sealRequired) {
      if (!row.sealOk && !row.sealJustification) {
        status = "fora_do_padrao";
        reasons.push(rules.rules.find(function (r) { return r.id === "rule-seal"; }).message);
      }
    }
    if (itemDef.tracksExpiry !== false && row.expiry) {
      var days = daysUntil(row.expiry);
      if (days != null) {
        if (days < 0) {
          status = "fora_do_padrao";
          reasons.push(rules.rules.find(function (r) { return r.id === "rule-expired"; }).message);
        } else if (days <= rules.expiryAlertDays) {
          if (status === "conforme") status = "alerta";
          reasons.push(rules.rules.find(function (r) { return r.id === "rule-alert-30"; }).message);
        } else if (days <= rules.expiryWarningDays) {
          if (status === "conforme") status = "alerta";
          reasons.push(rules.rules.find(function (r) { return r.id === "rule-warn-90"; }).message);
        }
      }
    }
    if (itemDef.qtySuggested && Number(row.qty) < Number(itemDef.qtySuggested)) {
      if (itemDef.highAlert) {
        status = "critico";
        reasons.push("Quantidade abaixo do mínimo sugerido para item de alta vigilância.");
      } else if (status === "conforme") {
        status = "alerta";
        reasons.push("Quantidade abaixo do mínimo sugerido — validar POP local.");
      }
    }
    return { status: status, reasons: reasons };
  }

  function defaultConference(manifest) {
    var rows = {};
    manifest.cartZones.forEach(function (zone) {
      zone.items.forEach(function (item) {
        rows[item.id] = {
          present: true,
          qty: item.qtySuggested,
          lot: "DEMO-" + item.id.slice(0, 6).toUpperCase(),
          expiry: item.tracksExpiry === false ? "" : addDaysISO(180),
          sealOk: true,
          sealJustification: ""
        };
      });
    });
    return {
      unit: "Hospital Demo",
      sector: "UTI Adulto",
      cartId: "CE-01",
      responsible: "Enf. Demo",
      rows: rows
    };
  }

  function loadConference(manifest) {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        var parsed = JSON.parse(raw);
        if (parsed && parsed.rows) return parsed;
      }
    } catch (e) {}
    return defaultConference(manifest);
  }

  function saveConference() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.conference));
    } catch (e) {}
  }

  function computeReport(manifest) {
    var rules = manifest.conferenceRules;
    var nc = [];
    var counts = { conforme: 0, alerta: 0, fora_do_padrao: 0, critico: 0, total: 0 };
    var itemStatus = {};
    manifest.cartZones.forEach(function (zone) {
      zone.items.forEach(function (item) {
        var row = state.conference.rows[item.id] || { present: false, qty: 0 };
        var ev = evaluateItem(item, row, rules);
        itemStatus[item.id] = ev;
        counts.total += 1;
        counts[ev.status] = (counts[ev.status] || 0) + 1;
        if (ev.status !== "conforme") {
          nc.push({
            zone: zone.title,
            item: item.name,
            status: ev.status,
            reasons: ev.reasons
          });
        }
      });
    });
    var conform = counts.conforme;
    var pct = counts.total ? Math.round((conform / counts.total) * 100) : 0;
    return { counts: counts, pct: pct, nc: nc, itemStatus: itemStatus };
  }

  function renderHero(manifest, root) {
    var el = $("#cko-cart-hero", root);
    if (!el) return;
    el.innerHTML =
      '<p class="cko-cart-hero__eyebrow">CKO-CART-001 · Equipamento de urgência</p>' +
      '<h1 class="cko-cart-hero__title">' + escapeHtml(manifest.document.title.split("|")[0].trim()) + "</h1>" +
      '<p class="cko-cart-hero__lead">' + escapeHtml(manifest.seo.description) + "</p>" +
      '<div class="cko-cart-chips">' +
      '<span class="cko-cart-chip">Explorador interativo</span>' +
      '<span class="cko-cart-chip">Conferência com validade</span>' +
      '<span class="cko-cart-chip">Export PDF · Excel · Word</span>' +
      '<span class="cko-cart-chip">Product · Inter + Nunito</span>' +
      "</div>";
  }

  function isMobileExplorer() {
    return window.matchMedia("(max-width: 960px)").matches;
  }

  function setPanelDrawerOpen(open) {
    var panel = $("#cko-zone-panel");
    var bd = $("#cko-panel-backdrop");
    var close = $("#cko-panel-close");
    if (panel) panel.classList.toggle("is-open", !!open);
    if (bd) {
      bd.classList.toggle("is-open", !!open);
      bd.hidden = !open;
    }
    if (close) close.style.display = open && isMobileExplorer() ? "inline-flex" : "none";
  }

  function renderExplorer(manifest, root) {
    var mount = $("#cko-cart-explorer", root);
    if (!mount) return;
    var imgAsset = manifest.assets.local.find(function (a) { return a.id === "cart-hero"; });
    var zones = manifest.cartZones;
    // Do not auto-select a zone on load — placeholder until click or ?zona=

    var tabs = zones.map(function (z) {
      return '<button type="button" class="cko-zone-tab' + (z.id === state.activeZone ? " is-active" : "") +
        '" data-zone="' + escapeHtml(z.id) + '">' + escapeHtml(z.shortLabel) + "</button>";
    }).join("");

    var spots = zones.map(function (z) {
      var h = z.hotspot;
      return (
        '<button type="button" class="cko-hotspot' + (z.id === state.activeZone ? " is-active" : "") +
        '" data-zone="' + escapeHtml(z.id) + '" style="left:' + h.xPercent + "%;top:" + h.yPercent +
        "%;width:" + h.widthPercent + "%;height:" + h.heightPercent +
        '%" aria-label="' + escapeHtml(z.title) + '">' +
        '<span class="cko-hotspot__label">' + escapeHtml(z.shortLabel) + "</span></button>"
      );
    }).join("");

    mount.innerHTML =
      '<div class="cko-cart-section">' +
      '<h2 class="cko-cart-section__title">Explorador do carrinho</h2>' +
      '<p class="cko-cart-section__sub">Clique nas zonas da ilustração ou use as abas. Deep-link: <code>?zona=</code></p>' +
      '<div class="cko-zone-tabs no-print">' + tabs + "</div>" +
      '<div class="cko-explorer">' +
      '<div class="cko-explorer__stage" id="cko-explorer-stage">' +
      '<img class="cko-explorer__img" src="' + escapeHtml(imgAsset.path) + '" width="' + (imgAsset.width || 1200) +
      '" height="' + (imgAsset.height || 900) + '" alt="' + escapeHtml(imgAsset.alt || "Carrinho") +
      '" fetchpriority="high" decoding="async" />' +
      spots +
      "</div>" +
      '<aside class="cko-panel" id="cko-zone-panel" aria-live="polite"></aside>' +
      "</div></div>" +
      '<div class="cko-drawer-backdrop" id="cko-panel-backdrop" hidden></div>';

    renderZonePanel(manifest, { openDrawer: false });
    bindExplorer(manifest);
  }

  function getZone(manifest, id) {
    if (!id) return null;
    return manifest.cartZones.find(function (z) { return z.id === id || z.deepLink === id; });
  }

  function renderZonePanel(manifest, opts) {
    opts = opts || {};
    var panel = $("#cko-zone-panel");
    if (!panel) return;
    var zone = getZone(manifest, state.activeZone);
    var shouldOpenDrawer = opts.openDrawer === true && !!zone;

    if (!zone) {
      panel.classList.remove("is-open");
      panel.classList.add("cko-panel--empty");
      panel.innerHTML =
        '<div class="cko-panel__empty">' +
        '<p class="cko-panel__empty-title">Selecione uma zona no carrinho</p>' +
        '<p class="cko-panel__empty-text">Clique em um hotspot ou aba para ver itens, quantidades sugeridas e alertas MAV.</p>' +
        "</div>";
      setPanelDrawerOpen(false);
      return;
    }

    panel.classList.remove("cko-panel--empty");
    var items = zone.items.map(function (it) {
      return (
        "<li><strong>" + escapeHtml(it.name) + "</strong>" +
        (it.highAlert ? ' <span class="cko-badge cko-badge--critico">MAV</span>' : "") +
        "<br>Qtd. sugerida: " + escapeHtml(it.qtySuggested) +
        (it.notes ? "<br><span style='color:#64748b'>" + escapeHtml(it.notes) + "</span>" : "") +
        "</li>"
      );
    }).join("");
    var mav = (zone.mavAlerts || []).map(function (m) { return "<div>" + escapeHtml(m) + "</div>"; }).join("");
    panel.innerHTML =
      '<h3 class="cko-panel__title">' + escapeHtml(zone.title) + "</h3>" +
      '<p class="cko-panel__summary">' + escapeHtml(zone.summary) + "</p>" +
      '<ul class="cko-panel__list">' + items + "</ul>" +
      (mav ? '<div class="cko-mav">' + mav + "</div>" : "") +
      '<p style="margin:.85rem 0 0;font-size:.78rem;color:#64748b">Deep-link: ?zona=' +
      escapeHtml(zone.deepLink) + "</p>" +
      '<button type="button" class="cko-btn cko-btn--ghost no-print" id="cko-panel-close" style="margin-top:.75rem;display:none">Fechar</button>';

    if (isMobileExplorer()) {
      setPanelDrawerOpen(shouldOpenDrawer);
    } else {
      setPanelDrawerOpen(false);
    }
  }

  function selectZone(manifest, id, pushUrl) {
    var zone = getZone(manifest, id);
    if (!zone) return;
    state.activeZone = zone.id;
    $all(".cko-hotspot, .cko-zone-tab").forEach(function (el) {
      el.classList.toggle("is-active", el.getAttribute("data-zone") === zone.id);
    });
    renderZonePanel(manifest, { openDrawer: true });
    announce("Zona selecionada: " + zone.title);
    if (pushUrl) {
      try {
        var url = new URL(window.location.href);
        url.searchParams.set("zona", zone.deepLink);
        history.replaceState(null, "", url.toString());
      } catch (e) {}
    }
  }

  function bindExplorer(manifest) {
    var root = $("#cko-cart-explorer");
    root.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-zone]");
      if (btn) {
        selectZone(manifest, btn.getAttribute("data-zone"), true);
      }
      if (e.target.id === "cko-panel-close" || e.target.id === "cko-panel-backdrop") {
        setPanelDrawerOpen(false);
      }
    });
  }

  function renderConference(manifest, root) {
    var mount = $("#cko-cart-tool", root);
    if (!mount) return;
    state.conference = loadConference(manifest);
    var report = computeReport(manifest);
    state.timestamp = new Date().toISOString();

    var meta =
      '<div class="cko-tool-meta">' +
      field("unit", "Unidade", state.conference.unit) +
      field("sector", "Setor", state.conference.sector) +
      field("cartId", "Identificação do carro", state.conference.cartId) +
      field("responsible", "Responsável", state.conference.responsible) +
      "</div>";

    function field(key, label, val) {
      return (
        '<div class="cko-field"><label for="cf-' + key + '">' + label + "</label>" +
        '<input id="cf-' + key + '" data-meta="' + key + '" value="' + escapeHtml(val) + '" /></div>'
      );
    }

    var drawers = manifest.cartZones.map(function (zone) {
      var rows = zone.items.map(function (item) {
        var row = state.conference.rows[item.id];
        var st = report.itemStatus[item.id];
        return (
          '<div class="cko-item" data-item="' + escapeHtml(item.id) + '">' +
          '<div class="cko-item__name">' + escapeHtml(item.name) +
          (item.highAlert ? ' <span class="cko-badge cko-badge--critico">MAV</span>' : "") + "</div>" +
          '<label><input type="checkbox" data-field="present"' + (row.present ? " checked" : "") + "> Presente</label>" +
          '<input type="number" min="0" data-field="qty" value="' + escapeHtml(row.qty) + '" title="Quantidade" />' +
          '<input type="text" data-field="lot" value="' + escapeHtml(row.lot || "") + '" placeholder="Lote" />' +
          '<input type="date" data-field="expiry" value="' + escapeHtml(row.expiry || "") + '" ' +
          (item.tracksExpiry === false ? "disabled" : "") + " />" +
          '<label><input type="checkbox" data-field="sealOk"' + (row.sealOk ? " checked" : "") +
          (item.tracksSeal ? "" : " disabled") + "> Lacre</label>" +
          '<span class="cko-badge cko-badge--' + st.status + '">' +
          escapeHtml(statusLabel(st.status, manifest.conferenceRules)) + "</span>" +
          "</div>"
        );
      }).join("");
      return (
        '<div class="cko-drawer-block"><div class="cko-drawer-block__head">' +
        escapeHtml(zone.title) + "</div>" + rows + "</div>"
      );
    }).join("");

    var ncHtml = report.nc.length
      ? "<ol class='cko-nc-list'>" + report.nc.map(function (n) {
          return "<li><strong>" + escapeHtml(n.item) + "</strong> (" + escapeHtml(n.zone) + "): " +
            escapeHtml(n.reasons.join(" ")) + "</li>";
        }).join("") + "</ol>"
      : "<p style='color:#15803d;font-weight:700'>Nenhuma não conformidade no momento.</p>";

    mount.innerHTML =
      '<div class="cko-cart-section" id="conferencia">' +
      '<h2 class="cko-cart-section__title">Ferramenta de conferência</h2>' +
      '<p class="cko-cart-section__sub">Checklist operacional com validade, lacre e status. Dados ficam só no seu navegador (demo).</p>' +
      meta +
      '<div class="cko-tool-actions no-print">' +
      '<button type="button" class="cko-btn cko-btn--primary" id="btn-recalc">Recalcular conformidade</button>' +
      '<button type="button" class="cko-btn cko-btn--danger" id="btn-simulate">Simular plantão com vencidos</button>' +
      '<button type="button" class="cko-btn cko-btn--ghost" id="btn-reset">Reset demo</button>' +
      '<button type="button" class="cko-btn cko-btn--primary" id="btn-export-pdf">Exportar PDF</button>' +
      '<button type="button" class="cko-btn cko-btn--ghost" id="btn-export-xlsx">Exportar Excel</button>' +
      '<button type="button" class="cko-btn cko-btn--ghost" id="btn-export-word">Exportar Word</button>' +
      "</div>" +
      '<div class="cko-summary-bar" id="cko-summary">' +
      stat("Conformidade", report.pct + "%") +
      stat("Alertas", report.counts.alerta) +
      stat("Fora do padrão", report.counts.fora_do_padrao) +
      stat("Críticos", report.counts.critico) +
      "</div>" +
      '<p style="font-size:.78rem;color:#64748b;margin:0 0 .75rem">Última avaliação: ' +
      escapeHtml(state.timestamp) + "</p>" +
      drawers +
      '<h3 style="color:var(--cart-navy);font-weight:900;margin:1rem 0 .5rem">Não conformidades e ações</h3>' +
      '<div id="cko-nc">' + ncHtml + "</div>" +
      "</div>";

    function stat(label, value) {
      return '<div class="cko-stat"><span class="cko-stat__label">' + label +
        '</span><span class="cko-stat__value">' + escapeHtml(value) + "</span></div>";
    }

    bindConference(manifest);
  }

  function readConferenceFromDom(manifest) {
    $all("[data-meta]").forEach(function (input) {
      state.conference[input.getAttribute("data-meta")] = input.value;
    });
    $all(".cko-item").forEach(function (row) {
      var id = row.getAttribute("data-item");
      if (!state.conference.rows[id]) state.conference.rows[id] = {};
      var r = state.conference.rows[id];
      var present = row.querySelector('[data-field="present"]');
      var qty = row.querySelector('[data-field="qty"]');
      var lot = row.querySelector('[data-field="lot"]');
      var expiry = row.querySelector('[data-field="expiry"]');
      var seal = row.querySelector('[data-field="sealOk"]');
      r.present = !!(present && present.checked);
      r.qty = qty ? Number(qty.value || 0) : 0;
      r.lot = lot ? lot.value : "";
      r.expiry = expiry ? expiry.value : "";
      r.sealOk = !!(seal && seal.checked);
    });
    saveConference();
  }

  function bindConference(manifest) {
    var mount = $("#cko-cart-tool");
    mount.addEventListener("change", function () {
      readConferenceFromDom(manifest);
    });
    mount.addEventListener("click", function (e) {
      var t = e.target;
      if (t.id === "btn-recalc") {
        readConferenceFromDom(manifest);
        renderConference(manifest, document);
        announce("Conformidade recalculada: " + computeReport(manifest).pct + "%");
      }
      if (t.id === "btn-simulate") {
        simulateExpired(manifest);
        renderConference(manifest, document);
        announce("Simulação de plantão com vencidos aplicada.");
      }
      if (t.id === "btn-reset") {
        state.conference = defaultConference(manifest);
        saveConference();
        renderConference(manifest, document);
        announce("Demo reiniciada.");
      }
      if (t.id === "btn-export-pdf") {
        readConferenceFromDom(manifest);
        exportPdf(manifest);
      }
      if (t.id === "btn-export-xlsx") {
        readConferenceFromDom(manifest);
        exportExcel(manifest);
      }
      if (t.id === "btn-export-word") {
        readConferenceFromDom(manifest);
        exportWord(manifest);
      }
    });
  }

  function simulateExpired(manifest) {
    var rows = state.conference.rows;
    if (rows.adrenalina) {
      rows.adrenalina.expiry = addDaysISO(-5);
      rows.adrenalina.lot = "VENC-AD";
    }
    if (rows.amiodarona) {
      rows.amiodarona.expiry = addDaysISO(20);
    }
    if (rows["eletrodos-dea"]) {
      rows["eletrodos-dea"].expiry = addDaysISO(-2);
    }
    if (rows["ambu-adulto"]) {
      rows["ambu-adulto"].present = true;
    }
    if (rows.lacre) {
      rows.lacre.sealOk = false;
      rows.lacre.sealJustification = "";
    }
    if (rows.bougie) {
      rows.bougie.present = false;
      rows.bougie.qty = 0;
    }
    if (rows.sf500) {
      rows.sf500.expiry = addDaysISO(60);
    }
    state.conference.sector = "Pronto-Socorro (simulado)";
    saveConference();
  }

  function loadScript(lib) {
    return new Promise(function (resolve, reject) {
      if (lib.id === "jspdf" && window.jspdf) return resolve();
      if (lib.id === "xlsx" && window.XLSX) return resolve();
      var s = document.createElement("script");
      s.src = lib.url;
      s.crossOrigin = lib.crossorigin || "anonymous";
      if (lib.integrity && lib.integrity.indexOf("PLACEHOLDER") === -1) {
        s.integrity = lib.integrity;
      }
      s.onload = function () { resolve(); };
      s.onerror = function () { reject(new Error("Falha ao carregar " + lib.id)); };
      document.head.appendChild(s);
    });
  }

  function getLib(manifest, id) {
    return (manifest.assets.externalLibraries || []).find(function (l) { return l.id === id; });
  }

  function formHeaderHtml(manifest, report) {
    var f = manifest.downloadableForms[0];
    var c = state.conference;
    return (
      '<div style="background:' + NAVY + ';color:#fff;padding:18px 20px;font-family:Arial,sans-serif">' +
      "<div style='font-size:11px;letter-spacing:.08em;text-transform:uppercase;opacity:.85'>Calculadoras de Enfermagem</div>" +
      "<div style='font-size:20px;font-weight:800;margin-top:4px'>" + escapeHtml(f.title) + "</div>" +
      "<div style='font-size:12px;margin-top:8px;opacity:.95'>Unidade: " + escapeHtml(c.unit) +
      " · Setor: " + escapeHtml(c.sector) + " · Carro: " + escapeHtml(c.cartId) +
      " · Responsável: " + escapeHtml(c.responsible) + "</div>" +
      "<div style='font-size:12px;margin-top:4px'>Conformidade: " + report.pct + "% · " +
      escapeHtml(state.timestamp || new Date().toISOString()) + "</div></div>"
    );
  }

  function exportPdf(manifest) {
    var report = computeReport(manifest);
    var lib = getLib(manifest, "jspdf");
    loadScript(lib).then(function () {
      var jsPDF = window.jspdf.jsPDF;
      var doc = new jsPDF({ unit: "pt", format: "a4" });
      doc.setFillColor(26, 62, 116);
      doc.rect(0, 0, 595, 72, "F");
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(9);
      doc.text("CALCULADORAS DE ENFERMAGEM", 40, 28);
      doc.setFontSize(14);
      doc.text(manifest.downloadableForms[0].title, 40, 48);
      doc.setTextColor(30, 41, 59);
      doc.setFontSize(10);
      var y = 96;
      var lines = [
        "Unidade: " + state.conference.unit,
        "Setor: " + state.conference.sector,
        "Carro: " + state.conference.cartId,
        "Responsável: " + state.conference.responsible,
        "Conformidade: " + report.pct + "%",
        "Timestamp: " + (state.timestamp || new Date().toISOString())
      ];
      lines.forEach(function (ln) { doc.text(ln, 40, y); y += 16; });
      y += 8;
      doc.setFont(undefined, "bold");
      doc.text("Itens", 40, y);
      doc.setFont(undefined, "normal");
      y += 18;
      manifest.cartZones.forEach(function (zone) {
        if (y > 760) { doc.addPage(); y = 48; }
        doc.setTextColor(26, 62, 116);
        doc.setFont(undefined, "bold");
        doc.text(zone.title, 40, y);
        doc.setFont(undefined, "normal");
        doc.setTextColor(30, 41, 59);
        y += 14;
        zone.items.forEach(function (item) {
          if (y > 770) { doc.addPage(); y = 48; }
          var row = state.conference.rows[item.id];
          var st = report.itemStatus[item.id].status;
          var line = "- " + item.name + " | " + (row.present ? "Presente" : "Ausente") +
            " | Qtd " + row.qty + " | Lote " + (row.lot || "-") + " | Val " + (row.expiry || "-") +
            " | " + st;
          var split = doc.splitTextToSize(line, 515);
          doc.text(split, 48, y);
          y += split.length * 12 + 2;
        });
        y += 8;
      });
      if (report.nc.length) {
        if (y > 700) { doc.addPage(); y = 48; }
        doc.setFont(undefined, "bold");
        doc.setTextColor(185, 28, 28);
        doc.text("Não conformidades", 40, y);
        y += 16;
        doc.setFont(undefined, "normal");
        doc.setTextColor(30, 41, 59);
        report.nc.forEach(function (n) {
          if (y > 770) { doc.addPage(); y = 48; }
          var t = doc.splitTextToSize("• " + n.item + " — " + n.reasons.join(" "), 515);
          doc.text(t, 40, y);
          y += t.length * 12 + 4;
        });
      }
      doc.setFontSize(8);
      doc.setTextColor(100, 116, 139);
      doc.text(manifest.downloadableForms[0].footerNote, 40, 820);
      doc.save("conferencia-carrinho-emergencia.pdf");
      announce("PDF exportado.");
    }).catch(function () {
      printFallback(manifest, report);
    });
  }

  function printFallback(manifest, report) {
    var w = window.open("", "_blank");
    if (!w) return;
    var body = formHeaderHtml(manifest, report) +
      '<div style="font-family:Arial,sans-serif;padding:20px;color:#1e293b">' +
      "<h2 style='color:" + NAVY + "'>Itens</h2><ul>" +
      manifest.cartZones.map(function (z) {
        return "<li><strong>" + escapeHtml(z.title) + "</strong><ul>" +
          z.items.map(function (it) {
            var r = state.conference.rows[it.id];
            return "<li>" + escapeHtml(it.name) + " — " + (r.present ? "Presente" : "Ausente") +
              ", qtd " + escapeHtml(r.qty) + ", val " + escapeHtml(r.expiry || "-") +
              ", status " + escapeHtml(report.itemStatus[it.id].status) + "</li>";
          }).join("") + "</ul></li>";
      }).join("") +
      "</ul><p style='font-size:11px;color:#64748b'>" +
      escapeHtml(manifest.downloadableForms[0].footerNote) + "</p></div>" +
      "<script>window.onload=function(){window.print()}<\/script>";
    w.document.write("<!doctype html><html><head><title>Conferência</title></head><body>" + body + "</body></html>");
    w.document.close();
    announce("Fallback de impressão aberto.");
  }

  function exportExcel(manifest) {
    var report = computeReport(manifest);
    var lib = getLib(manifest, "xlsx");
    loadScript(lib).then(function () {
      var header = [
        ["Calculadoras de Enfermagem"],
        [manifest.downloadableForms[0].title],
        ["Unidade", state.conference.unit],
        ["Setor", state.conference.sector],
        ["Carro", state.conference.cartId],
        ["Responsável", state.conference.responsible],
        ["Conformidade %", report.pct],
        ["Timestamp", state.timestamp]
      ];
      var items = [["Zona", "Item", "Presente", "Qtd", "Lote", "Validade", "Lacre", "Status"]];
      manifest.cartZones.forEach(function (z) {
        z.items.forEach(function (it) {
          var r = state.conference.rows[it.id];
          items.push([
            z.title, it.name, r.present ? "Sim" : "Não", r.qty, r.lot || "",
            r.expiry || "", r.sealOk ? "OK" : "Rompido", report.itemStatus[it.id].status
          ]);
        });
      });
      var nc = [["Item", "Zona", "Status", "Ação"]];
      report.nc.forEach(function (n) {
        nc.push([n.item, n.zone, n.status, n.reasons.join(" ")]);
      });
      var wb = window.XLSX.utils.book_new();
      window.XLSX.utils.book_append_sheet(wb, window.XLSX.utils.aoa_to_sheet(header), "Cabecalho");
      window.XLSX.utils.book_append_sheet(wb, window.XLSX.utils.aoa_to_sheet(items), "Itens");
      window.XLSX.utils.book_append_sheet(wb, window.XLSX.utils.aoa_to_sheet(nc), "Nao_conformidades");
      window.XLSX.writeFile(wb, "conferencia-carrinho-emergencia.xlsx");
      announce("Excel exportado.");
    }).catch(function () {
      exportCsvFallback(manifest, report);
    });
  }

  function exportCsvFallback(manifest, report) {
    var lines = ["Zona;Item;Presente;Qtd;Lote;Validade;Status"];
    manifest.cartZones.forEach(function (z) {
      z.items.forEach(function (it) {
        var r = state.conference.rows[it.id];
        lines.push([z.title, it.name, r.present ? "Sim" : "Nao", r.qty, r.lot || "", r.expiry || "", report.itemStatus[it.id].status].join(";"));
      });
    });
    var blob = new Blob(["\uFEFF" + lines.join("\n")], { type: "text/csv;charset=utf-8" });
    downloadBlob(blob, "conferencia-carrinho-emergencia.csv");
    announce("CSV de fallback exportado.");
  }

  function exportWord(manifest) {
    var report = computeReport(manifest);
    var rows = manifest.cartZones.map(function (z) {
      return "<h3 style='color:" + NAVY + "'>" + escapeHtml(z.title) + "</h3><table border='1' cellspacing='0' cellpadding='6' width='100%' style='border-collapse:collapse;font-size:12px'>" +
        "<tr style='background:#eff6ff'><th>Item</th><th>Presente</th><th>Qtd</th><th>Lote</th><th>Validade</th><th>Status</th></tr>" +
        z.items.map(function (it) {
          var r = state.conference.rows[it.id];
          return "<tr><td>" + escapeHtml(it.name) + "</td><td>" + (r.present ? "Sim" : "Não") +
            "</td><td>" + escapeHtml(r.qty) + "</td><td>" + escapeHtml(r.lot || "") +
            "</td><td>" + escapeHtml(r.expiry || "") + "</td><td>" +
            escapeHtml(report.itemStatus[it.id].status) + "</td></tr>";
        }).join("") + "</table>";
    }).join("");
    var nc = report.nc.map(function (n) {
      return "<li>" + escapeHtml(n.item) + " — " + escapeHtml(n.reasons.join(" ")) + "</li>";
    }).join("");
    var html =
      "<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word'>" +
      "<head><meta charset='utf-8'><title>Conferência</title></head><body>" +
      formHeaderHtml(manifest, report) +
      "<div style='font-family:Arial,sans-serif;padding:16px'>" + rows +
      "<h3 style='color:" + NAVY + "'>Não conformidades</h3><ul>" + (nc || "<li>Nenhuma</li>") +
      "</ul><p style='font-size:11px;color:#64748b'>" +
      escapeHtml(manifest.downloadableForms[0].footerNote) + "</p></div></body></html>";
    var blob = new Blob(["\ufeff", html], { type: "application/msword" });
    downloadBlob(blob, "conferencia-carrinho-emergencia.doc");
    announce("Word exportado.");
  }

  function downloadBlob(blob, filename) {
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () {
      URL.revokeObjectURL(a.href);
      a.remove();
    }, 500);
  }

  function copyrightNotice(manifest) {
    if (manifest.contentCopyright && manifest.contentCopyright.notice) {
      return manifest.contentCopyright.notice;
    }
    if (manifest.educationalArticle && manifest.educationalArticle.copyrightNotice) {
      return manifest.educationalArticle.copyrightNotice;
    }
    return "© Calculadoras de Enfermagem / Cia de Enfermagem Global Platform — direitos reservados. Uso educativo; adaptação ao POP local.";
  }

  function slugifyHeading(text) {
    var s = String(text || "").toLowerCase();
    if (typeof s.normalize === "function") {
      s = s.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    }
    return s.replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }

  function renderArticle(manifest, root) {
    var mount = $("#cko-cart-article", root);
    if (!mount || !manifest.educationalArticle) return;
    var art = manifest.educationalArticle;
    var articleOnly = root.getAttribute && root.getAttribute("data-cko-mode") === "article";
    var sections = (art.sections || []).map(function (sec) {
      var id = slugifyHeading(sec.heading);
      var paras = (sec.paragraphs || []).map(function (p) {
        return "<p>" + escapeHtml(p) + "</p>";
      }).join("");
      return (
        '<section class="cko-article__section" id="' + escapeHtml(id) + '">' +
        "<h3>" + escapeHtml(sec.heading) + "</h3>" +
        paras +
        "</section>"
      );
    }).join("");
    var fullLink = !articleOnly && art.href
      ? '<p class="cko-article__more"><a class="cko-btn cko-btn--primary" href="' +
        escapeHtml(art.href) + '">Abrir artigo completo</a></p>'
      : (articleOnly
        ? '<p class="cko-article__more"><a class="cko-btn cko-btn--ghost" href="/biblioteca-carinho-de-emergencia.html">Voltar ao carrinho interativo</a></p>'
        : "");
    var titleTag = articleOnly ? "h1" : "h2";
    mount.innerHTML =
      '<article class="cko-cart-section cko-article" aria-labelledby="cko-article-title">' +
      '<p class="cko-article__kicker">' + escapeHtml(art.kicker || "Conteúdo interno de direitos autorais") + "</p>" +
      '<p class="cko-cart-section__sub">' + escapeHtml(art.eyebrow || "Artigo educativo") + "</p>" +
      "<" + titleTag + ' class="cko-cart-section__title" id="cko-article-title">' +
      escapeHtml(art.title) + "</" + titleTag + ">" +
      '<p class="cko-article__lead">' + escapeHtml(art.lead || "") + "</p>" +
      sections +
      (art.legalReferencesNote
        ? '<p class="cko-article__legal">' + escapeHtml(art.legalReferencesNote) + "</p>"
        : "") +
      fullLink +
      '<footer class="cko-copyright">' + escapeHtml(copyrightNotice(manifest)) + "</footer>" +
      "</article>";
  }

  function renderTips(manifest, root) {
    var mount = $("#cko-cart-tips", root);
    if (!mount) return;
    var cards = manifest.tipsAndErrors.map(function (t) {
      return (
        '<article class="cko-tip-card cko-tip-card--' + t.type + '">' +
        "<h3>" + (t.type === "tip" ? "Dica · " : "Erro · ") + escapeHtml(t.title) + "</h3>" +
        "<p>" + escapeHtml(t.body) + "</p>" +
        (t.evidenceUrl
          ? '<a href="' + escapeHtml(t.evidenceUrl) + '" target="_blank" rel="noopener">' +
            escapeHtml(t.evidenceSource) + "</a>"
          : "<span>" + escapeHtml(t.evidenceSource) + "</span>") +
        "</article>"
      );
    }).join("");
    mount.innerHTML =
      '<div class="cko-cart-section"><h2 class="cko-cart-section__title">Dicas e erros comuns</h2>' +
      '<p class="cko-cart-section__sub">Orientação educativa original do site (conteúdo interno de direitos autorais). Normas externas aparecem só como referência legal breve.</p>' +
      '<div class="cko-tips-grid">' + cards + "</div>" +
      '<footer class="cko-copyright">' + escapeHtml(copyrightNotice(manifest)) + "</footer></div>";
  }

  function renderGuides(manifest, root) {
    var mount = $("#cko-cart-guides", root);
    if (!mount || !manifest.guidesArticles) return;
    var cards = manifest.guidesArticles.map(function (g) {
      var inner =
        '<div class="cko-related__kind">' + escapeHtml(g.kind || "guia") + "</div>" +
        "<h3>" + escapeHtml(g.title) + "</h3>" +
        "<p>" + escapeHtml(g.blurb || "") + "</p>";
      if (g.href) {
        return (
          '<a class="cko-tip-card cko-tip-card--tip cko-tip-card--link" href="' +
          escapeHtml(g.href) + '">' + inner + "</a>"
        );
      }
      return '<article class="cko-tip-card cko-tip-card--tip">' + inner + "</article>";
    }).join("");
    mount.innerHTML =
      '<div class="cko-cart-section"><h2 class="cko-cart-section__title">Guias e artigos do acervo</h2>' +
      '<div class="cko-tips-grid">' + cards + "</div>" +
      '<footer class="cko-copyright">' + escapeHtml(copyrightNotice(manifest)) + "</footer></div>";
  }

  function renderRelated(manifest, root) {
    var mount = $("#cko-cart-related", root);
    if (!mount) return;
    var cards = manifest.relatedContent.map(function (r) {
      return (
        '<a href="' + escapeHtml(r.href) + '">' +
        '<span class="cko-related__kind">' + escapeHtml(r.kind || "recurso") + "</span>" +
        "<strong>" + escapeHtml(r.title) + "</strong>" +
        "<span>" + escapeHtml(r.blurb || "") + "</span></a>"
      );
    }).join("");
    mount.innerHTML =
      '<div class="cko-cart-section"><h2 class="cko-cart-section__title">Conteúdos relacionados</h2>' +
      '<p class="cko-cart-section__sub">Trilhas transversais de PCR, TRR, checagem e equipamentos.</p>' +
      '<div class="cko-related">' + cards + "</div></div>";
  }

  function renderReferences(manifest, root) {
    var mount = $("#cko-cart-refs", root);
    if (!mount) return;
    var seals = {};
    (manifest.homologInstitutions.publicSeals || []).forEach(function (s) {
      seals[s.institutionId] = s;
    });
    var lis = manifest.references.map(function (r) {
      var seal = r.seal || (seals[r.institutionId] && seals[r.institutionId].seal);
      var label = seal === "fonte_homologada" ? "Fonte homologada" : seal === "leitura_complementar" ? "Leitura complementar" : "";
      return (
        "<li>" + escapeHtml(r.citation) +
        (label ? ' <span class="cko-seal cko-seal--' + seal + '">' + label + "</span>" : "") +
        '<br><a href="' + escapeHtml(r.url) + '" target="_blank" rel="noopener">' +
        escapeHtml(r.url) + "</a></li>"
      );
    }).join("");
    mount.innerHTML =
      '<div class="cko-cart-section"><h2 class="cko-cart-section__title">Referências</h2>' +
      '<p class="cko-cart-section__sub">Selos públicos apenas — critérios internos de homologação não são expostos.</p>' +
      '<ul class="cko-refs">' + lis + "</ul></div>";
  }

  function applyDeepLink(manifest) {
    try {
      var zona = new URL(window.location.href).searchParams.get("zona");
      if (zona) selectZone(manifest, zona, false);
    } catch (e) {}
  }

  function renderAll(manifest) {
    var root = $("#cko-cart-root") || document;
    var mode = root.getAttribute && root.getAttribute("data-cko-mode");
    if (mode === "article") {
      renderArticle(manifest, root);
      return;
    }
    renderHero(manifest, root);
    renderExplorer(manifest, root);
    renderConference(manifest, root);
    renderArticle(manifest, root);
    renderTips(manifest, root);
    renderGuides(manifest, root);
    renderRelated(manifest, root);
    renderReferences(manifest, root);
    applyDeepLink(manifest);
  }

  function boot() {
    var root = $("#cko-cart-root");
    fetch(MANIFEST_URL, { credentials: "same-origin" })
      .then(function (r) {
        if (!r.ok) throw new Error("Manifest HTTP " + r.status);
        return r.json();
      })
      .then(function (manifest) {
        state.manifest = manifest;
        renderAll(manifest);
        announce("Carrinho interativo carregado.");
      })
      .catch(function (err) {
        if (root) {
          root.innerHTML =
            '<div class="cko-cart-section"><h2 class="cko-cart-section__title">Falha ao carregar o recurso</h2>' +
            "<p>Não foi possível ler o manifesto CKO-CART-001. Sirva a pasta do site com <code>python -m http.server 8080</code> (não abra via file://).</p>" +
            "<pre style='font-size:12px;color:#b91c1c'>" + escapeHtml(err.message) + "\nURL: " + escapeHtml(MANIFEST_URL) + "</pre></div>";
        }
        console.error(err);
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
