/* ======================================================================
   partials-loader.js — Orquestrador de módulos via fetch()
   Calculadoras de Enfermagem — Global Platform
   ====================================================================== */
(function () {
  "use strict";

  var SCRIPT = document.currentScript;

  function detectBasePath() {
    if (SCRIPT && SCRIPT.src) {
      try {
        var url = new URL(SCRIPT.src, window.location.href);
        return url.pathname.replace(/js\/partials-loader\.js.*$/, "");
      } catch (e) { /* fall through */ }
    }
    var scripts = document.getElementsByTagName("script");
    for (var i = 0; i < scripts.length; i++) {
      var src = scripts[i].getAttribute("src") || "";
      if (src.indexOf("partials-loader.js") !== -1) {
        try {
          var u = new URL(src, window.location.href);
          return u.pathname.replace(/js\/partials-loader\.js.*$/, "");
        } catch (e2) { /* fall through */ }
      }
    }
    if (/\/html\//.test(window.location.pathname)) return "../";
    return "";
  }

  var BASE = detectBasePath();

  function assetPath(path) {
    if (/^(https?:|\/|data:|#)/.test(path)) return path;
    return BASE + path.replace(/^\.\//, "");
  }

  function rewritePartialPaths(html) {
    var base = BASE || "/";
    if (base.charAt(base.length - 1) !== "/") base += "/";
    return html.replace(
      /(\s(?:href|src|action)=["'])((?!\/|https?:|mailto:|#|javascript:|data:)[^"']*)/gi,
      function (_match, prefix, url) {
        return prefix + base + url.replace(/^\.\//, "");
      }
    );
  }

  function mountPartialHtml(target, html) {
    target.innerHTML = rewritePartialPaths(html);
    var modals = target.querySelectorAll(".ck-modal-overlay");
    for (var i = 0; i < modals.length; i++) {
      document.body.appendChild(modals[i]);
    }
  }

  function ensureChromeStyles() {
    var hasSiteStyles = document.querySelector(
      'link[rel="stylesheet"][href*="site-styles.css"]'
    );
    if (!hasSiteStyles) {
      var siteCss = document.createElement("link");
      siteCss.rel = "stylesheet";
      siteCss.href = assetPath("css/site-styles.css");
      document.head.appendChild(siteCss);
    }
  }

  function fixAssetLinks() {
    document.querySelectorAll('link[rel="stylesheet"][href^="css/"]').forEach(function (el) {
      var href = el.getAttribute("href");
      if (href && href.indexOf(BASE) !== 0 && BASE) el.href = assetPath(href);
    });
  }

  function showA11yBar() {
    var bar = document.getElementById("barraAcessibilidade");
    if (bar) bar.classList.add("show");
  }

  function injectFallbackHeader(target) {
    target.innerHTML =
      '<header class="rd-header"><div class="rd-container rd-header-inner">' +
      '<a href="' + assetPath("index.html") + '" class="rd-logo">' +
      '<span>Calculadoras de Enfermagem</span></a></div></header>';
  }

  var PARTIALS = [
    { url: assetPath("partials/header.html"), target: "site-header", fallback: injectFallbackHeader },
    { url: assetPath("partials/accessibility-toolbar.html"), target: "site-a11y" },
    { url: assetPath("partials/footer.html"), target: "site-footer" },
    { url: assetPath("partials/cookie-system.html"), target: "site-cookie" }
];;

  var DEPENDENT_SCRIPTS = [
    assetPath("js/global-scripts.js"),
    assetPath("js/mega-menu.js"),
    assetPath("js/i18n-loader.js"),
    assetPath("js/lang-selector.js"),
    assetPath("js/site-widgets.js")
  ];

  var COGNITIVE_SCRIPTS = [
    assetPath("js/cir/inference.js"),
    assetPath("js/nurse-palm.js"),
    assetPath("js/cognitive-ui.js")
  ];

  var CKO_PAGE_KEYS = {
    apgar: true,
    glasgow: true,
    "escala-de-glasgow": true
  };

  function needsCkoPipeline() {
    if (document.getElementById("tool-config")) return true;
    var page = document.body && document.body.getAttribute("data-page");
    return !!(page && CKO_PAGE_KEYS[page]);
  }

  function ckoScripts() {
    if (!needsCkoPipeline()) return [];
    return [
      assetPath("js/clinical-terminology.js"),
      assetPath("js/patient-context-storage.js"),
      assetPath("js/tool-cko-loader.js"),
      assetPath("js/tool-profile-engine.js"),
      assetPath("js/tool-footer-renderer.js"),
      assetPath("js/report-payload.js")
    ];
  }

  var CALC_ENGINE = assetPath("js/calc-engine-v2.js");

  function insertAfter(referenceEl, newEl) {
    if (!referenceEl || !referenceEl.parentNode || !newEl) return;
    if (referenceEl.nextSibling) {
      referenceEl.parentNode.insertBefore(newEl, referenceEl.nextSibling);
    } else {
      referenceEl.parentNode.appendChild(newEl);
    }
  }

  function ensureMount(id, parent, afterEl) {
    if (document.getElementById(id) || !parent) return document.getElementById(id);
    var el = document.createElement("div");
    el.id = id;
    if (afterEl) insertAfter(afterEl, el);
    else parent.appendChild(el);
    return el;
  }

  function buildFlowCard(id, title, icon, bodyHtml, attrs) {
    return (
      '<section class="calc-card flow-card' + (attrs && attrs.extraClass ? " " + attrs.extraClass : "") + '"' +
      (attrs && attrs.dataAttr ? " " + attrs.dataAttr : "") +
      ' aria-labelledby="' + id + '">' +
      '<div class="calc-card-header"><span class="bar" aria-hidden="true"></span>' +
      '<h2 id="' + id + '"><svg class="icon icon-sm"><use href="#' + icon + '"/></svg> ' + title + "</h2>" +
      (attrs && attrs.badge ? '<span class="cognitive-badge">' + attrs.badge + "</span>" : "") +
      "</div>" + bodyHtml + "</section>"
    );
  }

  function ensureClinicalFlowSections(flow) {
    if (!flow) return;
    flow.setAttribute("data-profile-clinical-flow", "");

    if (!document.getElementById("cognitivePanel")) {
      flow.insertAdjacentHTML("beforeend", buildFlowCard(
        "calcCogTitle",
        "Análise Cognitiva — Nurse-PaLM",
        "i-brain",
        '<div id="cognitivePanel" class="cognitive-panel cognitive-panel--embedded cip-hidden" data-cognitive-mount>' +
          '<div id="cognitivePanelContent" data-cognitive-panel-content></div>' +
        "</div>",
        { extraClass: "flow-card--cognitive cip-hidden", dataAttr: 'data-cog-section', badge: "Motor Clínico" }
      ));
    }

    if (!document.getElementById("calcMedicationSection")) {
      flow.insertAdjacentHTML("beforeend", buildFlowCard(
        "calcMedTitle",
        "Medicamentos — Base de Dados",
        "i-file",
        '<p class="med-link-band" id="calcMedBandLabel"></p>' +
        '<p class="flow-text" id="calcMedSummary"></p>' +
        '<div id="calcMedicationLinks" class="med-links-grid"></div>' +
        '<p class="med-link-disclaimer">Referência da base NKOS. Prescrição e administração dependem de avaliação médica e protocolo institucional.</p>',
        { dataAttr: 'id="calcMedicationSection" hidden' }
      ));
    }

    if (!document.getElementById("cipContainer")) {
      flow.insertAdjacentHTML("beforeend", buildFlowCard(
        "calcCipTitle",
        "Evidência & Pérolas Clínicas",
        "i-book",
        '<div id="cipContainer" class="cip-flow-inner cip-hidden" data-cip-mount></div>',
        { extraClass: "flow-card--cip cip-hidden", dataAttr: 'data-cip-section' }
      ));
    }

    if (!flow.querySelector("[data-kg-section]")) {
      flow.insertAdjacentHTML("beforeend", buildFlowCard(
        "calcKgTitle",
        "Recursos Conectados",
        "i-book",
        '<div class="cip-kg-links-list">' +
          '<a href="biblioteca.html" class="cip-kg-link"><i class="fa-solid fa-book"></i> Biblioteca de Recursos</a>' +
          '<a href="nurse-palm.html" class="cip-kg-link"><i class="fa-solid fa-brain"></i> Dashboard Nurse-PaLM</a>' +
          '<a href="diagnosticosnanda.html" class="cip-kg-link"><i class="fa-solid fa-clipboard-list"></i> NANDA-I</a>' +
          '<a href="sae.html" class="cip-kg-link"><i class="fa-solid fa-file-medical"></i> SAE</a>' +
          '<a href="medicamentos.html" class="cip-kg-link"><i class="fa-solid fa-pills"></i> Medicamentos</a>' +
          '<a href="protocolos.html" class="cip-kg-link"><i class="fa-solid fa-shield-halved"></i> Protocolos</a>' +
        "</div>",
        { extraClass: "flow-card--kg cip-hidden", dataAttr: 'data-kg-section' }
      ));
    }
  }

  function panelNeedsSharedMount(panelId, panel) {
    if (!panel || panelId === "padrao") return false;
    if (panelId === "estudante") return !panel.querySelector(".est-grid");
    if (panelId === "urgencia") return !panel.querySelector(".urg-panel");
    if (panelId === "academico") return !panel.querySelector(".aca-panel");
    if (panelId === "gestor") return !panel.querySelector(".gestor-grid");
    return true;
  }

  function pageHasInlineFooter() {
    var scope = document.getElementById("main-content") || document.querySelector("main") || document.body;
    return !!scope.querySelector(".learning-track-wrap, .tool-footer-zone, .tool-tags");
  }

  function normalizeToolShell() {
    if (!needsCkoPipeline()) return;

    var toolHeader = document.querySelector(".tool-header");
    if (toolHeader && !document.getElementById("patientContextPanel")) {
      ensureMount("patientContextMount", toolHeader.parentNode, toolHeader);
    }

    var profilePanels = document.querySelector('[data-tab-panels="perfil"]');
    if (profilePanels) {
      var order = ["padrao", "estudante", "urgencia", "gestor", "academico"];
      var padraoPanel = profilePanels.querySelector(':scope > .tab-panel[data-tab-panel="padrao"]');

      order.slice(1).forEach(function (panelId) {
        if (padraoPanel) {
          var nested = padraoPanel.querySelector(':scope > .tab-panel[data-tab-panel="' + panelId + '"]');
          if (nested) profilePanels.appendChild(nested);
        }
      });

      order.forEach(function (panelId) {
        var panel = profilePanels.querySelector(':scope > .tab-panel[data-tab-panel="' + panelId + '"]') ||
          document.querySelector('.tab-panel[data-tab-panel="' + panelId + '"]');
        if (!panel) return;
        if (panel.parentNode !== profilePanels) profilePanels.appendChild(panel);
      });
      order.forEach(function (panelId) {
        var panel = profilePanels.querySelector(':scope > .tab-panel[data-tab-panel="' + panelId + '"]');
        if (!panel) return;
        if (
          panelId !== "padrao" &&
          panelNeedsSharedMount(panelId, panel) &&
          !panel.querySelector('[data-profile-shared="' + panelId + '"]')
        ) {
          var mount = document.createElement("div");
          mount.setAttribute("data-profile-shared", panelId);
          panel.appendChild(mount);
        }
        if (panelId === "academico") {
          var saePanel = panel.querySelector('.aca-body [data-tab-panel="sae"]');
          if (saePanel) saePanel.classList.add("cognitive-locked");
        }
      });

      if (padraoPanel && !document.getElementById("toolFooterMount") && !pageHasInlineFooter()) {
        ensureMount("toolFooterMount", padraoPanel, null);
      }

      var flow = document.getElementById("calcClinicalFlow");
      var divider = document.getElementById("calcFlowDivider");
      if (flow && padraoPanel && padraoPanel.contains(flow)) {
        if (divider && padraoPanel.contains(divider)) {
          insertAfter(profilePanels, divider);
          insertAfter(divider, flow);
        } else {
          insertAfter(profilePanels, flow);
        }
      }
      ensureClinicalFlowSections(flow);
    }

    if (!document.getElementById("printTemplate")) {
      var siteFooter = document.getElementById("site-footer");
      var printMount = document.getElementById("printTemplateMount");
      if (!printMount) {
        printMount = document.createElement("div");
        printMount.id = "printTemplateMount";
        if (siteFooter && siteFooter.parentNode) {
          siteFooter.parentNode.insertBefore(printMount, siteFooter);
        } else {
          document.body.appendChild(printMount);
        }
      }
    }
  }

  function fetchPartial(item) {
    var target = document.getElementById(item.target);
    if (!target) return Promise.resolve();
    return fetch(item.url, { credentials: "same-origin" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status + " ao buscar " + item.url);
        return res.text();
      })
      .then(function (html) {
        mountPartialHtml(target, html);
        if (item.target === "site-a11y") showA11yBar();
      })
      .catch(function (err) {
        console.error("[partials-loader] Falha ao carregar", item.url, err);
        if (item.fallback) item.fallback(target);
      });
  }

  function loadScriptSequentially(src) {
    return new Promise(function (resolve) {
      if (document.querySelector('script[src="' + src + '"]')) {
        resolve();
        return;
      }
      var script = document.createElement("script");
      script.src = src;
      script.defer = false;
      script.onload = function () { resolve(); };
      script.onerror = function () {
        console.error("[partials-loader] Falha ao carregar script", src);
        resolve();
      };
      document.body.appendChild(script);
    });
  }

  function finishPartialsReady() {
    showA11yBar();
    document.dispatchEvent(new Event("partials:ready"));
  }

  function loadDependentScriptsInOrder(index) {
    if (index >= DEPENDENT_SCRIPTS.length) {
      if (document.getElementById("tool-config") || needsCkoPipeline()) {
        loadCkoThenCognitive();
        return;
      }
      finishPartialsReady();
      return;
    }
    loadScriptSequentially(DEPENDENT_SCRIPTS[index]).then(function () {
      loadDependentScriptsInOrder(index + 1);
    });
  }

  function loadScriptsList(list, idx, onDone) {
    idx = idx || 0;
    if (idx >= list.length) {
      onDone();
      return;
    }
    loadScriptSequentially(list[idx]).then(function () {
      loadScriptsList(list, idx + 1, onDone);
    });
  }

  function loadCognitiveScriptsThenCalcEngine(idx) {
    idx = idx || 0;
    if (idx >= COGNITIVE_SCRIPTS.length) {
      var ckoReady = window.ToolCKO && window.ToolCKO.ready
        ? window.ToolCKO.ready
        : Promise.resolve();
      var termReady = window.ClinicalTerminology && window.ClinicalTerminology.ready
        ? window.ClinicalTerminology.ready()
        : Promise.resolve();
      Promise.all([ckoReady, termReady]).then(function () {
        loadScriptSequentially(CALC_ENGINE).then(finishPartialsReady);
      });
      return;
    }
    loadScriptSequentially(COGNITIVE_SCRIPTS[idx]).then(function () {
      loadCognitiveScriptsThenCalcEngine(idx + 1);
    });
  }

  function loadCkoThenCognitive() {
    var list = ckoScripts();
    loadScriptsList(list, 0, function () {
      loadCognitiveScriptsThenCalcEngine(0);
    });
  }

  function loadPrintTemplate() {
    if (document.getElementById("printTemplate")) return Promise.resolve();
    var mount = document.getElementById("printTemplateMount");
    if (!mount) return Promise.resolve();
    return fetch(assetPath("partials/relatorio-fiel.html"), { credentials: "same-origin" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status + " ao buscar relatorio-fiel");
        return res.text();
      })
      .then(function (html) {
        mount.innerHTML = rewritePartialPaths(html);
        document.dispatchEvent(new Event("print-template:ready"));
      })
      .catch(function (err) {
        console.error("[partials-loader] Falha ao carregar relatorio-fiel", err);
      });
  }

  function loadPatientContextPanel() {
    if (document.getElementById("patientContextPanel")) return Promise.resolve();
    var mount = document.getElementById("patientContextMount");
    if (!mount) return Promise.resolve();
    return fetch(assetPath("partials/patient-context-panel.html"), { credentials: "same-origin" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status + " ao buscar patient-context-panel");
        return res.text();
      })
      .then(function (html) {
        mount.innerHTML = rewritePartialPaths(html);
        document.dispatchEvent(new Event("patient-context:ready"));
      })
      .catch(function (err) {
        console.error("[partials-loader] Falha ao carregar patient-context-panel", err);
      });
  }

  function init() {
    ensureChromeStyles();
    fixAssetLinks();
    normalizeToolShell();
    Promise.all(PARTIALS.map(fetchPartial))
      .then(function () { return loadPatientContextPanel(); })
      .then(function () { return loadPrintTemplate(); })
      .then(function () {
        document.body.classList.add("has-site-chrome");
        loadDependentScriptsInOrder(0);
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
