/* ======================================================================
   patient-context-storage.js — Dados do paciente em localStorage
   Chave: patientContext → { name, reg, age, bed }
   ====================================================================== */
(function (global) {
  "use strict";

  var STORAGE_KEY = "patientContext";

  function read() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    } catch (e) {
      return {};
    }
  }

  function write(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    document.dispatchEvent(new CustomEvent("patient-context:updated", { detail: data }));
  }

  function bindField(id, key) {
    var el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("input", function () {
      var data = read();
      data[key] = el.value.trim();
      write(data);
    });
    el.addEventListener("change", function () {
      var data = read();
      data[key] = el.value.trim();
      write(data);
      if (global.showToast) global.showToast("Dados do paciente salvos no navegador", "success");
    });
  }

  function fillForm(data) {
    var map = {
      patientName: "name",
      patientReg: "reg",
      patientAge: "age",
      patientBed: "bed"
    };
    Object.keys(map).forEach(function (id) {
      var el = document.getElementById(id);
      if (el && data[map[id]]) el.value = data[map[id]];
    });
    var status = document.getElementById("patientContextStatus");
    if (status) {
      status.textContent = data.name ? "Salvo: " + data.name : "Preencha e os dados ficam no localStorage deste navegador.";
    }
  }

  function clearForm() {
    localStorage.removeItem(STORAGE_KEY);
    ["patientName", "patientReg", "patientAge", "patientBed"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.value = "";
    });
    fillForm({});
    if (global.showToast) global.showToast("Dados do paciente removidos", "info");
  }

  function init() {
    var panel = document.getElementById("patientContextPanel");
    if (!panel) return;
    fillForm(read());
    bindField("patientName", "name");
    bindField("patientReg", "reg");
    bindField("patientAge", "age");
    bindField("patientBed", "bed");
    var clearBtn = document.getElementById("patientContextClear");
    if (clearBtn) clearBtn.addEventListener("click", clearForm);
  }

  global.PatientContextStorage = { read: read, write: write, clear: clearForm };

  document.addEventListener("patient-context:ready", init);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : globalThis);
