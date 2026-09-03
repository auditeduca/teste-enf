/**
 * CKO Page Templates — aplica identidade por tipo (home | institutional | calculator | tool | content).
 *
 * <body data-cko-template="calculator" class="cko-cart-page">
 */
(function () {
  "use strict";

  var CONFIG_PATH = "/data/cko-page-templates.json";
  var configCache = null;

  function siteUrl(absPath) {
    if (window.CKOPageShell && typeof window.CKOPageShell.siteUrl === "function") {
      return window.CKOPageShell.siteUrl(absPath);
    }
    var path = String(absPath || "").replace(/^\//, "");
    try {
      var parts = window.location.pathname.replace(/\\/g, "/").split("/").filter(Boolean);
      if (parts.length && /\.[a-z0-9]+$/i.test(parts[parts.length - 1])) parts.pop();
      var prefix = parts.map(function () { return ".."; }).join("/");
      return (prefix ? prefix + "/" : "") + path;
    } catch (e) {
      return "/" + path;
    }
  }

  function getTemplateId() {
    var body = document.body;
    if (!body) return null;
    return (
      body.getAttribute("data-cko-template") ||
      (document.querySelector("[data-cko-template]") &&
        document.querySelector("[data-cko-template]").getAttribute("data-cko-template")) ||
      null
    );
  }

  function applyBodyClass(tplId, tplDef) {
    var body = document.body;
    if (!body || !tplId) return;
    body.setAttribute("data-cko-template", tplId);
    if (tplDef && tplDef.bodyClass && body.className.indexOf(tplDef.bodyClass) === -1) {
      body.className += (body.className ? " " : "") + tplDef.bodyClass;
    }
    if (body.className.indexOf("cko-cart-page") === -1 && tplId !== "home") {
      // home also benefits from token alignment
      body.className += " cko-cart-page";
    }
    if (tplId === "home" && body.className.indexOf("cko-cart-page") === -1) {
      body.className += " cko-cart-page";
    }
  }

  function ensureMainId() {
    var main = document.querySelector("main");
    if (main && !main.id) main.id = "main-content";
    if (main && main.className.indexOf("cko-tpl-main") === -1) {
      main.className += (main.className ? " " : "") + "cko-tpl-main";
    }
  }

  function validateStructure(tplId, tplDef) {
    var issues = [];
    if (!tplDef) {
      issues.push({ severity: "error", code: "unknown-template", message: "Template desconhecido: " + tplId });
      return issues;
    }
    if (!document.getElementById("main-content") && !document.querySelector("main")) {
      issues.push({ severity: "error", code: "main", message: "<main> ausente" });
    }
    if (tplDef.shell) {
      ["chrome", "hero", "sidebar"].forEach(function (slot) {
        if (!document.querySelector('[data-cko-slot="' + slot + '"]')) {
          issues.push({
            severity: "warn",
            code: "slot-" + slot,
            message: "slot " + slot + " ausente no template " + tplId
          });
        }
      });
      if (!document.querySelector(".cko-layout")) {
        issues.push({ severity: "error", code: "layout", message: "cko-layout obrigatório" });
      }
    }
    if (tplId === "calculator") {
      if (!document.querySelector("[data-cko-calc-form], form, .cko-calc-workspace, .cko-calc-panel")) {
        issues.push({
          severity: "warn",
          code: "calc-form",
          message: "Área de formulário da calculadora não marcada"
        });
      }
    }
    if (tplId === "scale") {
      if (!document.querySelector("[data-cko-scale-items], .cko-scale-grid")) {
        issues.push({
          severity: "warn",
          code: "scale-items",
          message: "Área de itens da escala não marcada"
        });
      }
      if (document.querySelector('[class*="-card-navy"] h1, [data-cko-static="hero"], section.hero, .tool-header')) {
        issues.push({
          severity: "error",
          code: "scale-local-hero",
          message: "Escala fora do padrão: hero local (navy/static) — use o slot hero do shell"
        });
      }
    }
    if (tplId === "home") {
      if (!document.querySelector("[data-cko-home='hero'], .cko-home-hero")) {
        issues.push({
          severity: "info",
          code: "home-hero",
          message: "Marque o hero com data-cko-home=\"hero\" ou .cko-home-hero"
        });
      }
    }
    return issues;
  }

  function markReady(tplId, issues) {
    var body = document.body;
    if (!body) return;
    body.setAttribute("data-cko-tpl-ready", "1");
    if (issues && issues.length) {
      body.setAttribute(
        "data-cko-tpl-issues",
        issues
          .map(function (i) {
            return i.code;
          })
          .join(",")
      );
    }
    try {
      document.dispatchEvent(
        new CustomEvent("cko-template:ready", {
          detail: { template: tplId, issues: issues || [] }
        })
      );
    } catch (e) {}
  }

  function run(config) {
    var tplId = getTemplateId();
    if (!tplId) return;
    var tplDef = config.templates && config.templates[tplId];
    applyBodyClass(tplId, tplDef);
    ensureMainId();
    var issues = validateStructure(tplId, tplDef);
    markReady(tplId, issues);
    if (issues.some(function (i) { return i.severity === "error"; })) {
      console.warn("[CKO templates]", issues);
    }
  }

  function boot() {
    var tplId = getTemplateId();
    if (!tplId) return;

    if (configCache) {
      run(configCache);
      return;
    }

    fetch(siteUrl(CONFIG_PATH), { credentials: "same-origin" })
      .then(function (r) {
        if (!r.ok) throw new Error("templates config HTTP " + r.status);
        return r.json();
      })
      .then(function (cfg) {
        configCache = cfg;
        run(cfg);
      })
      .catch(function (err) {
        // Soft-fail: still apply body class from attribute
        applyBodyClass(tplId, { bodyClass: "cko-tpl-" + tplId });
        ensureMainId();
        markReady(tplId, [{ severity: "warn", code: "config", message: String(err) }]);
        console.error(err);
      });
  }

  window.CKOPageTemplates = {
    boot: boot,
    getTemplateId: getTemplateId,
    getConfig: function () {
      return configCache;
    },
    validate: function () {
      var tplId = getTemplateId();
      if (!tplId || !configCache) return [];
      return validateStructure(tplId, configCache.templates[tplId]);
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
