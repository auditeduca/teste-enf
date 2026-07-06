(function () {
  "use strict";

  var STORAGE_KEY = "sbar-draft-v1";
  var STEPS = ["Situação", "Background", "Avaliação", "Recomendação"];
  var state = load();

  function load() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "null") || fresh();
    } catch (e) {
      return fresh();
    }
  }
  function fresh() {
    return { patient: null, step: 0, showPatient: true, situation: "", background: "", assessment: "", recommendation: "" };
  }
  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }
  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function mount() {
    var root = document.getElementById("wizard-app");
    if (!root) return;
    root.innerHTML = renderShell();
    bind();
  }

  function renderShell() {
    var patientLine = state.patient ? esc(state.patient.name) + " · " + esc(state.patient.medicalRecord) : "Identifique o paciente";
    var stepper = STEPS.map(function (label, i) {
      var cls = "wizard-step" + (i === state.step ? " active" : "") + (i < state.step ? " done" : "");
      return '<button type="button" class="' + cls + '" data-step="' + i + '"><span class="wizard-step-num">' + ["S", "B", "A", "R"][i] + "</span><span>" + label + "</span></button>";
    }).join("");
    return (
      '<div class="wizard-panel"><div class="wizard-top"><div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px">' +
      "<div><h2>Comunicação SBAR</h2><p class=\"wizard-patient\">" + patientLine + "</p></div>" +
      '<button type="button" class="btn btn-blue" id="sbar-save">Salvar</button></div>' +
      '<div class="wizard-stepper">' + stepper + "</div></div>" +
      '<div class="wizard-body" id="sbar-body">' + renderBody() + "</div></div>"
    );
  }

  function field(id, label, val) {
    return "<label>" + esc(label) + '<textarea data-field="' + id + '">' + esc(val || "") + "</textarea></label>";
  }

  function renderBody() {
    if (state.showPatient || !state.patient) {
      var p = state.patient || {};
      return (
        '<form id="sbar-patient" class="wizard-form"><h3>Paciente</h3>' +
        "<label>Nome *<input required data-f=\"name\" value=\"" + esc(p.name || "") + '"></label>' +
        '<div class="wizard-grid-2"><label>Prontuário *<input required data-f="mr" value="' + esc(p.medicalRecord || "") + '"></label>' +
        '<label>Diagnóstico<input data-f="dx" value="' + esc(p.diagnosis || "") + '"></label></div>' +
        '<div class="wizard-actions"><span></span><button class="btn btn-blue" type="submit">Iniciar SBAR</button></div></form>'
      );
    }
    var html = '<div class="wizard-form">';
    if (state.step === 0) html += field("situation", "S — Situação (o que está acontecendo agora?)", state.situation);
    if (state.step === 1) html += field("background", "B — Background (contexto clínico relevante)", state.background);
    if (state.step === 2) html += field("assessment", "A — Avaliação (sua análise clínica)", state.assessment);
    if (state.step === 3) {
      html += field("recommendation", "R — Recomendação (o que você sugere ou precisa?)", state.recommendation);
      html += '<div class="wizard-summary"><strong>Preview SBAR</strong><br>S: ' + esc(state.situation) + "<br>B: " + esc(state.background) + "<br>A: " + esc(state.assessment) + "<br>R: " + esc(state.recommendation) + "</div>";
    }
    html += '<div class="wizard-actions">' + (state.step ? '<button type="button" class="btn btn-outline-navy" id="sbar-prev">Anterior</button>' : "<span></span>");
    html += state.step < 3 ? '<button type="button" class="btn btn-blue" id="sbar-next">Próximo</button>' : '<button type="button" class="btn btn-blue" id="sbar-done">Finalizar</button>';
    html += "</div></div>";
    return html;
  }

  function collect() {
    var body = document.getElementById("sbar-body");
    body.querySelectorAll("[data-field]").forEach(function (el) {
      state[el.getAttribute("data-field")] = el.value;
    });
  }

  function bind() {
    var pf = document.getElementById("sbar-patient");
    if (pf) {
      pf.addEventListener("submit", function (e) {
        e.preventDefault();
        state.patient = {
          name: pf.querySelector('[data-f="name"]').value,
          medicalRecord: pf.querySelector('[data-f="mr"]').value,
          diagnosis: pf.querySelector('[data-f="dx"]').value,
        };
        state.showPatient = false;
        save();
        mount();
      });
    }
    document.querySelectorAll(".wizard-step").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var s = parseInt(btn.getAttribute("data-step"), 10);
        if (s <= state.step) { collect(); state.step = s; save(); mount(); }
      });
    });
    var n = document.getElementById("sbar-next");
    if (n) n.addEventListener("click", function () { collect(); state.step++; save(); mount(); });
    var p = document.getElementById("sbar-prev");
    if (p) p.addEventListener("click", function () { collect(); state.step--; save(); mount(); });
    var d = document.getElementById("sbar-done");
    if (d) d.addEventListener("click", function () { collect(); save(); alert("SBAR registrado localmente."); });
    var s = document.getElementById("sbar-save");
    if (s) s.addEventListener("click", function () { collect(); save(); alert("Rascunho salvo."); });
  }

  document.addEventListener("partials:ready", mount);
  if (document.readyState !== "loading") mount();
})();
