/* ======================================================================
   clinical-terminology.js — Resolve NANDA/NIC/NOC por código (Fase 1.2)
   Fonte: js/bundles/clinical-terminology.{locale}.json (gerado por build)
   ====================================================================== */
(function (global) {
  "use strict";

  var SCRIPT = document.currentScript;
  function detectBasePath() {
    if (SCRIPT && SCRIPT.src) {
      try {
        var url = new URL(SCRIPT.src, window.location.href);
        return url.pathname.replace(/js\/clinical-terminology\.js.*$/, "");
      } catch (e) { /* fall through */ }
    }
    if (/\/html\//.test(window.location.pathname)) return "../";
    return "";
  }
  var BASE = detectBasePath();
  var BUNDLE_URL = BASE + "js/bundles/clinical-terminology.pt-BR.json";
  var cache = null;
  var loadPromise = null;

  function normalizeCode(kind, code) {
    if (code == null || code === "") return "";
    var s = String(code).replace(/^NANDA\.|^NIC\.|^NOC\./i, "");
    if (kind === "nanda" || kind === "noc") {
      return s.length <= 5 ? s.padStart(5, "0") : s;
    }
    return s;
  }

  function fetchBundle() {
    if (cache) return Promise.resolve(cache);
    if (loadPromise) return loadPromise;
    loadPromise = fetch(BUNDLE_URL)
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (json) {
        cache = json;
        return json;
      })
      .catch(function (err) {
        console.warn("[clinical-terminology] bundle não carregado:", err);
        cache = { nanda: {}, nic: {}, noc: {} };
        return cache;
      });
    return loadPromise;
  }

  function lookup(kind, code) {
    if (!cache || !code) return null;
    var key = normalizeCode(kind, code);
    var table = cache[kind] || {};
    return table[key] || table[String(code)] || table[String(code).replace(/^0+/, "")] || null;
  }

  function label(kind, code, locale) {
    var rec = lookup(kind, code);
    if (!rec) return "";
    locale = locale || (document.documentElement.lang || "pt-BR");
    var ll = rec.localized_labels || {};
    return ll[locale] || ll["pt-BR"] || rec.label || "";
  }

  function enrichEntry(kind, entry, locale) {
    if (!entry || typeof entry !== "object") return entry;
    var code = entry.code || entry.nanda_code || entry.nic_code || entry.noc_code;
    if (!code) return entry;
    var rec = lookup(kind, code);
    if (!rec) return entry;
    locale = locale || "pt-BR";
    var out = Object.assign({}, entry);
    var lbl = label(kind, code, locale);
    if (kind === "nanda") {
      out.diagnosis = out.diagnosis || lbl;
      out.name = out.name || lbl;
      out.definition = out.definition || rec.definition || "";
    } else if (kind === "nic") {
      out.intervention = out.intervention || lbl;
      out.name = out.name || lbl;
    } else if (kind === "noc") {
      out.outcome = out.outcome || lbl;
      out.name = out.name || lbl;
    }
    out.code = code;
    return out;
  }

  function enrichSae(sae, locale) {
    if (!sae) return { nanda: [], nic: [], noc: [] };
    return {
      nanda: (sae.nanda || []).map(function (n) { return enrichEntry("nanda", n, locale); }),
      nic: (sae.nic || []).map(function (n) { return enrichEntry("nic", n, locale); }),
      noc: (sae.noc || []).map(function (n) { return enrichEntry("noc", n, locale); }),
    };
  }

  function ready() {
    return fetchBundle();
  }

  global.ClinicalTerminology = {
    ready: ready,
    fetchBundle: fetchBundle,
    lookup: function (kind, code) { return lookup(kind, code); },
    label: label,
    enrichSae: enrichSae,
    normalizeCode: normalizeCode,
  };
})(typeof window !== "undefined" ? window : globalThis);
