(function () {
  "use strict";

  var STORAGE_KEY = "cv-draft-v1";
  var STEPS = ["Dados pessoais", "Experiência", "Competências", "Layout", "Exportar"];
  var state = load();

  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "null") || { step: 0, personal: {}, experience: "", skills: "", template: "classic" }; }
    catch (e) { return { step: 0, personal: {}, experience: "", skills: "", template: "classic" }; }
  }
  function save() { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }
  function esc(s) { var d = document.createElement("div"); d.textContent = s == null ? "" : String(s); return d.innerHTML; }

  function mount() {
    var root = document.getElementById("wizard-app");
    if (!root) return;
    root.innerHTML = render();
    bind();
  }

  function render() {
    var stepper = STEPS.map(function (l, i) {
      return '<button type="button" class="wizard-step' + (i === state.step ? " active" : "") + (i < state.step ? " done" : "") + '" data-step="' + i + '"><span class="wizard-step-num">' + (i + 1) + "</span>" + l + "</button>";
    }).join("");
    return '<div class="wizard-panel"><div class="wizard-top"><h2>Gerador de Currículo</h2><div class="wizard-stepper">' + stepper + '</div></div><div class="wizard-body" id="cv-body">' + stepContent() + "</div></div>";
  }

  function f(id, label, val) {
    return "<label>" + esc(label) + '<input data-f="' + id + '" value="' + esc(val || "") + '"></label>';
  }

  function stepContent() {
    var p = state.personal;
    var html = '<div class="wizard-form">';
    if (state.step === 0) {
      html += f("fullName", "Nome completo", p.fullName) + f("title", "Título profissional", p.title);
      html += '<div class="wizard-grid-2">' + f("email", "E-mail", p.email) + f("phone", "Telefone", p.phone) + "</div>";
      html += "<label>Resumo<textarea data-f=\"summary\">" + esc(p.summary || "") + "</textarea></label>";
    } else if (state.step === 1) {
      html += "<label>Experiência profissional<textarea data-f=\"experience\">" + esc(state.experience || "") + "</textarea></label>";
      html += "<label>Formação acadêmica<textarea data-f=\"education\">" + esc(state.education || "") + "</textarea></label>";
    } else if (state.step === 2) {
      html += "<label>Competências e certificações<textarea data-f=\"skills\">" + esc(state.skills || "") + "</textarea></label>";
    } else if (state.step === 3) {
      html += '<label>Modelo<select data-f="template"><option value="classic"' + (state.template === "classic" ? " selected" : "") + '>Clássico</option><option value="modern"' + (state.template === "modern" ? " selected" : "") + ">Moderno</option></select></label>";
    } else {
      html += '<div class="wizard-summary" id="cv-preview"><h3 style="margin-bottom:8px">' + esc(p.fullName || "Seu nome") + "</h3><p>" + esc(p.title || "") + "</p><hr style=\"margin:12px 0;border:none;border-top:1px solid var(--line)\"><p>" + esc(p.summary || "") + "</p><h4 style=\"margin-top:12px\">Experiência</h4><p>" + esc(state.experience || "") + "</p><h4 style=\"margin-top:12px\">Competências</h4><p>" + esc(state.skills || "") + "</p></div>";
      html += '<button type="button" class="btn btn-blue" id="cv-print">Imprimir / Salvar PDF</button>';
    }
    html += '<div class="wizard-actions">' + (state.step ? '<button type="button" class="btn btn-outline-navy" id="cv-prev">Anterior</button>' : "<span></span>");
    html += state.step < 4 ? '<button type="button" class="btn btn-blue" id="cv-next">Próximo</button>' : "";
    html += "</div></div>";
    return html;
  }

  function collect() {
    document.querySelectorAll("#cv-body [data-f]").forEach(function (el) {
      var k = el.getAttribute("data-f");
      if (["fullName", "title", "email", "phone", "summary"].indexOf(k) !== -1) {
        state.personal[k] = el.value;
      } else {
        state[k] = el.value;
      }
    });
  }

  function bind() {
    document.querySelectorAll(".wizard-step").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var s = +btn.getAttribute("data-step");
        if (s <= state.step) { collect(); state.step = s; save(); mount(); }
      });
    });
    var n = document.getElementById("cv-next");
    if (n) n.addEventListener("click", function () { collect(); state.step++; save(); mount(); });
    var p = document.getElementById("cv-prev");
    if (p) p.addEventListener("click", function () { collect(); state.step--; save(); mount(); });
    var pr = document.getElementById("cv-print");
    if (pr) pr.addEventListener("click", function () { window.print(); });
  }

  document.addEventListener("partials:ready", mount);
  if (document.readyState !== "loading") mount();
})();
