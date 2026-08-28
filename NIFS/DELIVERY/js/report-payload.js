/**
 * report-payload.js — Monta o JSON do relatório a partir da página da calculadora.
 * Compatível com POST /generate-report da API (NIFS/DELIVERY/api/report_server.py).
 */
(function (global) {
  "use strict";

  function domText(id, fallback) {
    var el = document.getElementById(id);
    if (!el) return fallback != null ? fallback : "";
    var t = (el.textContent || "").replace(/\s+/g, " ").trim();
    if (!t || t === "—") return fallback != null ? fallback : "";
    return t;
  }

  function readPatientContext() {
    try {
      return JSON.parse(localStorage.getItem("patientContext") || "{}");
    } catch (e) {
      return {};
    }
  }

  function readToolHeader() {
    var header = document.querySelector(".tool-header");
    if (!header) return {};
    var h1 = header.querySelector("h1");
    var badge = header.querySelector(".tool-category-badge");
    var subtitle = header.querySelector(".tool-subtitle");
    return {
      name: h1 ? h1.textContent.trim() : "",
      category: badge ? badge.textContent.trim() : "",
      subtitle: subtitle ? subtitle.textContent.trim() : ""
    };
  }

  function readParametersFromForm() {
    var form = document.getElementById("calcForm");
    if (!form) return [];
    var rows = [];
    form.querySelectorAll(".field-row").forEach(function (row) {
      var labelEl = row.querySelector(".field-label");
      var input = row.querySelector("[data-calc-input]");
      if (!labelEl || !input) return;
      var id = input.getAttribute("data-calc-input");
      var label = labelEl.textContent.trim();
      var scoreBox = document.querySelector('[data-formula-box="' + id + '"]');
      var score = scoreBox ? scoreBox.textContent.trim() : "";
      if (!score && input.tagName === "SELECT") {
        score = input.options[input.selectedIndex].text.trim();
      }
      rows.push({ label: label, score: score || input.value });
    });
    return rows;
  }

  function readListTexts(listId) {
    var list = document.getElementById(listId);
    if (!list) return [];
    return Array.prototype.slice.call(list.querySelectorAll("li")).map(function (li) {
      return (li.textContent || "").replace(/\s+/g, " ").trim();
    }).filter(Boolean);
  }

  function readReference() {
    var refLi = document.querySelector('[data-tab-panel="referencias"] .ref-list li, .ref-list li');
    if (!refLi) return "";
    var clone = refLi.cloneNode(true);
    var num = clone.querySelector(".ref-num");
    if (num) num.remove();
    return (clone.textContent || "").replace(/\s+/g, " ").trim();
  }

  function riskFromBanner() {
    var banner = document.getElementById("calcStatusBanner");
    if (!banner) return "unknown";
    if (banner.classList.contains("danger") || banner.classList.contains("critical")) return "critical";
    if (banner.classList.contains("warning")) return "moderate";
    if (banner.classList.contains("success")) return "none";
    return "unknown";
  }

  /**
   * @param {object} [opts]
   * @param {string} [opts.toolSlug]
   * @param {object} [opts.config] — objeto CONFIG do calc-engine (opcional)
   */
  function buildReportPayload(opts) {
    opts = opts || {};
    var now = new Date();
    var header = readToolHeader();
    var patient = readPatientContext();
    var config = opts.config || {};
    var overview = config.overview || {};
    var formula = (config.calculator && config.calculator.formula) || {};

    var score = domText("calcResultValue");
    var total = null;
    var scoreMax = formula.scoreMax;
    if (scoreMax == null && config.interpretation && config.interpretation.ranges) {
      config.interpretation.ranges.forEach(function (r) {
        if (r.max != null && (total == null || r.max > total)) total = r.max;
      });
    } else if (scoreMax != null) {
      total = scoreMax;
    }

    var nanda = domText("calcNandaText");
    var nic = domText("calcNicText");
    var noc = domText("calcNocText");
    var flow = document.getElementById("calcClinicalFlow");
    var showNnn = flow && flow.classList.contains("is-visible") && (nanda || nic || noc);

    var ipsg = readListTexts("calcSafetyIpsgList").map(function (text, idx) {
      return { tag: "M" + (idx + 1), text: text };
    });

  return {
      report_info: {
        title: "Relatório de Resultado",
        date: now.toLocaleDateString("pt-BR"),
        time: now.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }),
        exam_name: header.name || overview.name || document.title,
        exam_description: header.category || overview.categoryBadge || ""
      },
      patient: {
        name: patient.name || "—",
        reg: patient.reg || patient.id || "—",
        age: patient.age || "—",
        bed: patient.bed || patient.location || "—"
      },
      parameters: readParametersFromForm(),
      result: {
        score: score,
        total: total,
        unit: domText("calcResultUnit", formula.resultUnit || "pontos"),
        classification: domText("calcStatusTitle"),
        risk_level: riskFromBanner()
      },
      clinical_interpretation: domText("calcStatusText"),
      clinical_nnn: showNnn ? { nanda: nanda, nic: nic, noc: noc } : null,
      safety_ipsg: ipsg.length ? ipsg : undefined,
      safety_meds: readListTexts("calcSafetyMedsList"),
      reference: readReference() || undefined,
      responsible: { name: "Enf. Responsável", id: "COREN: _______" },
      tool_slug: opts.toolSlug || config.slug || undefined
    };
  }

  /**
   * Envia payload para a API e abre HTML em nova aba.
   * @param {string} apiBase — ex: http://localhost:8000
   * @param {object} [opts]
   */
  function generateReportViaApi(apiBase, opts) {
    var payload = buildReportPayload(opts);
    return fetch(apiBase.replace(/\/$/, "") + "/generate-report?embed_css=1", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }).then(function (res) {
      if (!res.ok) throw new Error("API " + res.status);
      return res.text();
    }).then(function (html) {
      var w = window.open("", "_blank");
      if (w) {
        w.document.write(html);
        w.document.close();
      }
      return html;
    });
  }

  global.ReportPayload = {
    build: buildReportPayload,
    generateViaApi: generateReportViaApi
  };
})(typeof window !== "undefined" ? window : globalThis);
