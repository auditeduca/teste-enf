/* ======================================================================
   tool-cko-loader.js — Carrega Clinical Knowledge Object e funde com tool-config
   ====================================================================== */
(function () {
  "use strict";

  var SCRIPT = document.currentScript;
  var CKO_MAP = {
    apgar: "js/modules/data/apgar-cko.json"
  };
  var CKO_SOURCE_V3 = {
    apgar: "js/modules/data/cko/CKO-APGAR-001.json"
  };

  function detectBasePath() {
    if (SCRIPT && SCRIPT.src) {
      try {
        var url = new URL(SCRIPT.src, window.location.href);
        return url.pathname.replace(/js\/tool-cko-loader\.js.*$/, "");
      } catch (e) { /* fall through */ }
    }
    if (/\/html\//.test(window.location.pathname)) return "../";
    return "";
  }

  var BASE = detectBasePath();

  function assetPath(path) {
    if (/^(https?:|\/|data:|#)/.test(path)) return path;
    return BASE + path.replace(/^\.\//, "");
  }

  function getToolKey() {
    var body = document.body;
    if (!body) return null;
    var key = body.getAttribute("data-tool-cko");
    if (key) return key;
    var page = body.getAttribute("data-page");
    if (page && CKO_MAP[page]) return page;
    return null;
  }

  function parseToolConfig() {
    var el = document.getElementById("tool-config");
    if (!el) return null;
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      console.error("[tool-cko-loader] tool-config inválido", e);
      return null;
    }
  }

  function deepMerge(target, source) {
    if (!source || typeof source !== "object") return target;
    Object.keys(source).forEach(function (key) {
      var sv = source[key];
      var tv = target[key];
      if (sv && typeof sv === "object" && !Array.isArray(sv) && tv && typeof tv === "object" && !Array.isArray(tv)) {
        deepMerge(tv, sv);
      } else if (sv !== undefined) {
        target[key] = sv;
      }
    });
    return target;
  }

  function mergeCkoWithConfig(cko, config) {
    var merged = JSON.parse(JSON.stringify(config || {}));
    if (cko.metadata) {
      merged.id = cko.metadata.id || merged.id;
      merged.code = cko.metadata.code || merged.code;
      merged.slug = cko.metadata.slug || merged.slug;
      merged.version = cko.metadata.version || merged.version;
      merged.status = cko.metadata.status || merged.status;
      if (cko.metadata.seo) merged.seo = deepMerge(merged.seo || {}, cko.metadata.seo);
      if (cko.metadata.breadcrumb) merged.breadcrumb = cko.metadata.breadcrumb;
    }
    if (cko.reasoning && cko.reasoning.sae) merged.sae = cko.reasoning.sae;
    if (cko.evidence) merged.evidence = deepMerge(merged.evidence || {}, cko.evidence);
    if (cko.presentation && cko.presentation.learning) merged.learning = cko.presentation.learning;
    merged._cko = cko;
    return merged;
  }

  function loadJson(url) {
    return fetch(url, { credentials: "same-origin" }).then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status + " — " + url);
      return res.json();
    });
  }

  function init() {
    var key = getToolKey();
    if (!key || !CKO_MAP[key]) {
      window.ToolCKO = { ready: Promise.resolve(null), data: null, config: parseToolConfig() };
      return;
    }

    var configEl = document.getElementById("tool-config");
    var ckoUrl = assetPath(CKO_MAP[key]);

    window.ToolCKO = {
      data: null,
      config: null,
      edges: null,
      ready: loadJson(ckoUrl)
        .then(function (cko) {
          window.ToolCKO.data = cko;
          window.ToolCKO.sourceV3 = CKO_SOURCE_V3[key] || null;
          var baseConfig = parseToolConfig() || {};
          var merged = mergeCkoWithConfig(cko, baseConfig);
          window.ToolCKO.config = merged;
          if (configEl) configEl.textContent = JSON.stringify(merged);
          var edgesFile = cko.reasoning && cko.reasoning.edges_file;
          if (!edgesFile) return cko;
          return loadJson(assetPath(edgesFile))
            .then(function (edges) {
              window.ToolCKO.edges = edges;
              return cko;
            })
            .catch(function () {
              return cko;
            });
        })
        .catch(function (err) {
          console.warn("[tool-cko-loader] CKO não carregado, usando tool-config:", err);
          window.ToolCKO.config = parseToolConfig();
          return null;
        })
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
