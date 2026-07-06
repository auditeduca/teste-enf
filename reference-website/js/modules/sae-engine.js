(function () {
  "use strict";

  var STORAGE_KEY = "sae-draft-v1";
  var STEPS = ["Coleta de Dados", "Diagnóstico", "Planejamento", "Implementação", "Avaliação"];

  var NANDA = [
    { id: "n1", code: "00032", title: "Risco de Queda", domain: "Segurança/Proteção", definition: "Susceptibilidade a quedas que podem causar dano físico." },
    { id: "n2", code: "00202", title: "Lesão por Pressão", domain: "Segurança/Proteção", definition: "Lesão localizada na pele e/ou tecido subjacente." },
    { id: "n3", code: "00132", title: "Dor Aguda", domain: "Conforto", definition: "Experiência sensorial e emocional desagradável." },
    { id: "n4", code: "00054", title: "Ansiedade", domain: "Percepção/Cognição", definition: "Sensação vaga de desconforto ou apreensão." },
    { id: "n5", code: "00002", title: "Risco de Infecção", domain: "Segurança/Proteção", definition: "Risco de invasão por organismos patogênicos." },
  ];

  var state = load();

  function load() {
    try {
      var s = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      if (s) return s;
    } catch (e) {}
    return { patient: null, step: 0, showPatient: true, data: {}, diagnoses: [], plan: "", implementation: "", evaluation: "" };
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
    var patientLine = "";
    if (state.patient) {
      patientLine = esc(state.patient.name) + " · Prontuário " + esc(state.patient.medicalRecord) + " · " + esc(state.patient.age) + " anos";
    }
    var stepper = STEPS.map(function (label, i) {
      var cls = "wizard-step" + (i === state.step ? " active" : "") + (i < state.step ? " done" : "");
      return '<button type="button" class="' + cls + '" data-step="' + i + '"><span class="wizard-step-num">' + (i + 1) + "</span><span>" + label + "</span></button>";
    }).join("");

    return (
      '<div class="wizard-panel">' +
      '<div class="wizard-top"><div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap">' +
      "<div><h2>Assistente SAE</h2><p class=\"wizard-patient\">" + (patientLine || "Identifique o paciente para iniciar") + "</p></div>" +
      '<button type="button" class="btn btn-blue" id="sae-save-draft">Salvar rascunho</button></div>' +
      '<div class="wizard-stepper">' + stepper + "</div></div>" +
      '<div class="wizard-body" id="sae-step-body">' + renderStepBody() + "</div></div>"
    );
  }

  function renderStepBody() {
    if (state.showPatient || !state.patient) return renderPatientForm();
    if (state.step === 0) return renderDataCollection();
    if (state.step === 1) return renderDiagnosis();
    if (state.step === 2) return renderPlanning();
    if (state.step === 3) return renderImplementation();
    return renderEvaluation();
  }

  function field(label, id, value, type) {
    type = type || "text";
    if (type === "textarea") {
      return "<label>" + esc(label) + '<textarea data-field="' + id + '">' + esc(value || "") + "</textarea></label>";
    }
    return "<label>" + esc(label) + '<input type="' + type + '" data-field="' + id + '" value="' + esc(value || "") + '"></label>';
  }

  function renderPatientForm() {
    var p = state.patient || {};
    return (
      '<form id="sae-patient-form" class="wizard-form">' +
      "<h3>Identificação do paciente</h3>" +
      field("Nome completo *", "name", p.name) +
      '<div class="wizard-grid-2">' + field("Idade *", "age", p.age, "number") + field("Prontuário *", "medicalRecord", p.medicalRecord) + "</div>" +
      '<div class="wizard-grid-2">' + field("Leito", "bed", p.bed) + field("Unidade", "unit", p.unit) + "</div>" +
      '<div class="wizard-actions"><span></span><button type="submit" class="btn btn-blue">Iniciar SAE</button></div></form>'
    );
  }

  function renderDataCollection() {
    var d = state.data;
    return (
      '<div class="wizard-form">' +
      field("Queixa principal", "chiefComplaint", d.chiefComplaint, "textarea") +
      field("História da doença atual", "hpi", d.hpi, "textarea") +
      field("Antecedentes", "history", d.history, "textarea") +
      field("Medicações em uso", "meds", d.meds, "textarea") +
      field("Alergias", "allergies", d.allergies) +
      '<div class="wizard-grid-2">' + field("PA sistólica", "pas", d.pas, "number") + field("PA diastólica", "pad", d.pad, "number") + "</div>" +
      '<div class="wizard-grid-2">' + field("FC", "fc", d.fc, "number") + field("SpO₂ (%)", "spo2", d.spo2, "number") + "</div>" +
      navButtons(true)
    );
  }

  function renderDiagnosis() {
    var list = NANDA.map(function (n) {
      var sel = state.diagnoses.indexOf(n.id) !== -1 ? " checked" : "";
      return (
        '<label class="catalog-card" style="display:block;margin-bottom:10px;cursor:pointer">' +
        '<input type="checkbox" data-nanda="' + n.id + '"' + sel + "> " +
        "<strong>" + esc(n.code) + " — " + esc(n.title) + "</strong><p>" + esc(n.definition) + "</p></label>"
      );
    }).join("");
    return "<div><h3>Diagnósticos NANDA-I</h3>" + list + navButtons(true) + "</div>";
  }

  function renderPlanning() {
    return (
      '<div class="wizard-form">' +
      field("Resultados esperados (NOC)", "plan", state.plan, "textarea") +
      field("Intervenções (NIC)", "nic", state.nic, "textarea") +
      navButtons(true) +
      "</div>"
    );
  }

  function renderImplementation() {
    return (
      '<div class="wizard-form">' +
      field("Intervenções executadas", "implementation", state.implementation, "textarea") +
      field("Observações", "implNotes", state.implNotes, "textarea") +
      navButtons(true) +
      "</div>"
    );
  }

  function renderEvaluation() {
    return (
      '<div class="wizard-form">' +
      field("Resposta do paciente", "evaluation", state.evaluation, "textarea") +
      field("Ajustes no plano", "adjustment", state.adjustment, "textarea") +
      '<div class="wizard-summary"><strong>Resumo:</strong> ' + esc(state.diagnoses.length) + " diagnóstico(s) registrado(s).</div>" +
      navButtons(false, true) +
      "</div>"
    );
  }

  function navButtons(showPrev, finish) {
    return (
      '<div class="wizard-actions">' +
      (state.step > 0 ? '<button type="button" class="btn btn-outline-navy" id="sae-prev">Anterior</button>' : "<span></span>") +
      (finish ? '<button type="button" class="btn btn-blue" id="sae-finish">Concluir SAE</button>' : '<button type="button" class="btn btn-blue" id="sae-next">Próxima etapa</button>') +
      "</div>"
    );
  }

  function collectFields(container) {
    container.querySelectorAll("[data-field]").forEach(function (el) {
      state.data[el.getAttribute("data-field")] = el.value;
      if (el.getAttribute("data-field") === "chiefComplaint") state.data.chiefComplaint = el.value;
    });
    var map = { chiefComplaint: "chiefComplaint", hpi: "hpi", history: "history", meds: "meds", allergies: "allergies", pas: "pas", pad: "pad", fc: "fc", spo2: "spo2", plan: "plan", nic: "nic", implementation: "implementation", implNotes: "implNotes", evaluation: "evaluation", adjustment: "adjustment" };
    container.querySelectorAll("[data-field]").forEach(function (el) {
      var k = el.getAttribute("data-field");
      state[k in state ? k : "data"] = el.value;
      if (k in map) state[map[k] === "chiefComplaint" ? k : k] = el.value;
      state.data[k] = el.value;
      if (k === "plan") state.plan = el.value;
      if (k === "nic") state.nic = el.value;
      if (k === "implementation") state.implementation = el.value;
      if (k === "implNotes") state.implNotes = el.value;
      if (k === "evaluation") state.evaluation = el.value;
      if (k === "adjustment") state.adjustment = el.value;
    });
  }

  function bind() {
    var body = document.getElementById("sae-step-body");
    var form = document.getElementById("sae-patient-form");
    if (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var fd = new FormData(form);
        state.patient = {
          name: form.querySelector('[data-field="name"]').value,
          age: form.querySelector('[data-field="age"]').value,
          medicalRecord: form.querySelector('[data-field="medicalRecord"]').value,
          bed: form.querySelector('[data-field="bed"]').value,
          unit: form.querySelector('[data-field="unit"]').value,
        };
        state.showPatient = false;
        state.step = 0;
        save();
        mount();
      });
    }
    document.querySelectorAll(".wizard-step").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var s = parseInt(btn.getAttribute("data-step"), 10);
        if (s <= state.step) {
          collectFields(body);
          state.step = s;
          save();
          mount();
        }
      });
    });
    var next = document.getElementById("sae-next");
    if (next) next.addEventListener("click", function () {
      collectFields(body);
      body.querySelectorAll("[data-nanda]").forEach(function (cb) {
        var id = cb.getAttribute("data-nanda");
        if (cb.checked && state.diagnoses.indexOf(id) === -1) state.diagnoses.push(id);
        if (!cb.checked) state.diagnoses = state.diagnoses.filter(function (x) { return x !== id; });
      });
      state.step = Math.min(state.step + 1, STEPS.length - 1);
      save();
      mount();
    });
    var prev = document.getElementById("sae-prev");
    if (prev) prev.addEventListener("click", function () {
      collectFields(body);
      state.step = Math.max(state.step - 1, 0);
      save();
      mount();
    });
    var finish = document.getElementById("sae-finish");
    if (finish) finish.addEventListener("click", function () {
      collectFields(body);
      save();
      alert("SAE concluída e salva localmente neste dispositivo.");
    });
    var draft = document.getElementById("sae-save-draft");
    if (draft) draft.addEventListener("click", function () {
      collectFields(body);
      save();
      alert("Rascunho salvo.");
    });
  }

  document.addEventListener("partials:ready", mount);
  if (document.readyState !== "loading") mount();
})();
