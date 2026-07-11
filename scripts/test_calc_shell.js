#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const { JSDOM } = require(path.join(__dirname, "..", "NIFS", "DELIVERY", "node_modules", "jsdom"));

const ROOT = path.join(__dirname, "..", "NIFS", "DELIVERY");
const PAGES = ["wells-tvp.html", "imc.html", "nihss.html", "apgar.html", "glasgow.html"];

function runPage(file) {
  const filePath = path.join(ROOT, file);
  const html = fs.readFileSync(filePath, "utf8");
  const dom = new JSDOM(html, { url: "file://" + filePath, pretendToBeVisual: true });
  const { window } = dom;
  const ctx = require("vm").createContext(window);
  Object.defineProperty(window.document, "readyState", { get: () => "complete" });
  window.fetch = () => Promise.resolve({ ok: false, text: () => Promise.resolve("") });
  require("vm").runInContext(fs.readFileSync(path.join(ROOT, "js/partials-loader.js"), "utf8"), ctx);

  const { document } = window;
  const profilePanels = document.querySelector('[data-tab-panels="perfil"]');
  const gestor = document.querySelector('.tab-panel[data-tab-panel="gestor"]');
  const flow = document.getElementById("calcClinicalFlow");
  const issues = [];

  if (!profilePanels) issues.push("sem data-tab-panels=perfil");
  if (gestor && profilePanels && !profilePanels.contains(gestor)) {
    issues.push("gestor fora das abas de perfil");
  }
  if (flow && profilePanels && profilePanels.contains(flow)) {
    issues.push("calcClinicalFlow ainda dentro das abas");
  }
  if (!document.getElementById("patientContextMount") && !document.getElementById("patientContextPanel")) {
    issues.push("sem patient context mount/panel");
  }

  const padrao = profilePanels && profilePanels.querySelector(':scope > .tab-panel[data-tab-panel="padrao"]');
  if (padrao && padrao.querySelector(':scope > .tab-panel[data-tab-panel="estudante"]')) {
    issues.push("estudante ainda aninhado em padrao");
  }

  document.querySelectorAll("[data-profile-shared]").forEach((mount) => {
    const id = mount.getAttribute("data-profile-shared");
    const panel = mount.closest('[data-tab-panel="' + id + '"]');
    if (panel && panel.querySelector(".est-grid, .urg-panel, .aca-panel, .gestor-grid")) {
      issues.push("mount duplicado em perfil com HTML inline: " + id);
    }
  });

  return { file, issues, sharedMounts: document.querySelectorAll("[data-profile-shared]").length };
}

let failed = 0;
for (const file of PAGES) {
  const res = runPage(file);
  if (res.issues.length) {
    failed++;
    console.log("FAIL", file, res.issues.join("; "));
  } else {
    console.log("OK", file, "(mounts:", res.sharedMounts + ")");
  }
}
process.exit(failed ? 1 : 0);
