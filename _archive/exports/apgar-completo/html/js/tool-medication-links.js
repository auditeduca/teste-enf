/* ======================================================================
   tool-medication-links.js — Medicamentos contextuais por escore da ferramenta
   ====================================================================== */
(function () {
  "use strict";

  var SCRIPT = document.currentScript;
  var DATA_FILE = "js/modules/data/apgar-medications.json";
  var data = null;
  var root = null;

  function detectBasePath() {
    if (SCRIPT && SCRIPT.src) {
      try {
        var url = new URL(SCRIPT.src, window.location.href);
        return url.pathname.replace(/js\/tool-medication-links\.js.*$/, "");
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

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function bandForScore(score) {
    if (!data || !data.bands) return null;
    for (var i = 0; i < data.bands.length; i++) {
      var b = data.bands[i];
      if (score >= b.min && score <= b.max) return b;
    }
    return null;
  }

  function medBySlug(slug) {
    return data && data.medications ? data.medications[slug] : null;
  }

  function renderCard(med) {
    var alertBadge = med.high_alert_medication
      ? '<span class="med-link-badge med-link-badge--alert">Alta vigilância</span>'
      : "";
    var note = med.context_note_pt || med.definition_pt || "";
    if (note.length > 160) note = note.slice(0, 157) + "…";
    return (
      '<a class="related-tool-card med-link-card" href="' +
      esc(assetPath(med.calc_href || "medicamentos.html")) +
      '">' +
      '<div class="icon-wrap"><svg class="icon"><use href="#i-pills"/></svg></div>' +
      "<div>" +
      "<h3>" +
      esc(med.term_pt) +
      "</h3>" +
      '<p class="med-link-meta">' +
      esc(med.class_label_pt || med.pharmacological_class || "") +
      alertBadge +
      "</p>" +
      "<p>" +
      esc(note) +
      "</p>" +
      "</div></a>"
    );
  }

  function gridHtml(band) {
    var slugs = band.slugs || [];
    if (!slugs.length) {
      return (
        '<p class="med-link-empty">' +
        esc(band.summary_pt || "Nenhuma medicação de urgência indicada para este escore.") +
        ' <a href="' +
        esc(assetPath("protocolos.html")) +
        '">Ver protocolos</a> · <a href="' +
        esc(assetPath("medicamentos.html")) +
        '">Calculadora de medicamentos</a></p>'
      );
    }
    return slugs
      .map(function (slug) {
        var med = medBySlug(slug);
        return med ? renderCard(med) : "";
      })
      .filter(Boolean)
      .join("");
  }

  function fillMount(mount, band) {
    var bandEl = mount.querySelector("[data-profile-med-band]");
    var summaryEl = mount.querySelector("[data-profile-med-summary]");
    var gridEl = mount.querySelector("[data-profile-med-grid]");
    if (bandEl) bandEl.textContent = band.label;
    if (summaryEl) summaryEl.textContent = band.summary_pt || "";
    if (gridEl) gridEl.innerHTML = gridHtml(band);
    mount.hidden = false;
  }

  function render(score) {
    if (!data) return;
    var band = bandForScore(score);
    var profileMounts = document.querySelectorAll("[data-profile-med-mount]");

    if (!band) {
      if (root) root.hidden = true;
      profileMounts.forEach(function (m) { m.hidden = true; });
      return;
    }

    var html = gridHtml(band);
    var section = document.getElementById("calcMedicationSection");
    var title = document.getElementById("calcMedBandLabel");
    var summary = document.getElementById("calcMedSummary");
    var grid = document.getElementById("calcMedicationLinks");

    if (title) title.textContent = band.label;
    if (summary) summary.textContent = band.summary_pt || "";
    if (grid) grid.innerHTML = html;
    if (section) section.hidden = false;
    if (root) root.hidden = false;

    profileMounts.forEach(function (mount) {
      fillMount(mount, band);
    });
  }

  function readScore() {
    var el = document.getElementById("calcResultValue");
    if (!el) return null;
    var n = parseInt(String(el.textContent).trim(), 10);
    return isNaN(n) ? null : n;
  }

  function onCalculate() {
    var score = readScore();
    if (score == null) return;
    render(score);
  }

  function bindForm() {
    var form = document.getElementById("calcForm");
    if (form) form.addEventListener("submit", function () {
      window.requestAnimationFrame(onCalculate);
    });

    var resultEl = document.getElementById("calcResultValue");
    if (resultEl && window.MutationObserver) {
      var obs = new MutationObserver(onCalculate);
      obs.observe(resultEl, { childList: true, characterData: true, subtree: true });
    }
  }

  function init() {
    root = document.getElementById("calcMedicationSection");
    if (!root && !document.querySelector("[data-profile-med-mount]")) return;

    fetch(assetPath(DATA_FILE), { credentials: "same-origin" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (json) {
        data = json;
        bindForm();
        var initial = readScore();
        if (initial != null && document.getElementById("calcClinicalFlow") &&
            document.getElementById("calcClinicalFlow").classList.contains("is-visible")) {
          render(initial);
        }
      })
      .catch(function (err) {
        console.error("[tool-medication-links]", err);
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
