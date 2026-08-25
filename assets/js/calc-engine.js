/* CKO calc-engine — interactive scoring for generated pages. No CDN. */
(function () {
  "use strict";

  var configEl = document.getElementById("tool-config");
  var CONFIG = {};
  if (configEl) {
    try {
      CONFIG = JSON.parse(configEl.textContent);
    } catch (err) {
      console.error("calc-engine: invalid #tool-config", err);
    }
  }

  var inputsCfg = (CONFIG.calculator && CONFIG.calculator.inputs) || [];
  var formulaCfg = (CONFIG.calculator && CONFIG.calculator.formula) || { type: "none" };
  var ranges = (CONFIG.interpretation && CONFIG.interpretation.ranges) || [];
  var decimals = typeof formulaCfg.decimals === "number" ? formulaCfg.decimals : 0;
  var state = {};

  inputsCfg.forEach(function (inp) {
    state[inp.id] = inp.defaultValue !== undefined ? inp.defaultValue : 0;
  });

  function fields(id) {
    return Array.prototype.slice.call(document.querySelectorAll('[data-calc-input="' + id + '"]'));
  }

  function scoreOf(inputId) {
    var inp = inputsCfg.filter(function (item) { return item.id === inputId; })[0];
    if (!inp) return 0;
    var val = state[inputId];
    if (inp.type === "select" && inp.options) {
      var opt = inp.options.filter(function (item) { return String(item.value) === String(val); })[0];
      if (!opt) return 0;
      return opt.score !== undefined ? Number(opt.score) : Number(opt.value);
    }
    return Number(val) || 0;
  }

  function safeEval(expr) {
    if (!/^[0-9+\-*/().\s]+$/.test(expr)) return NaN;
    try {
      return Function('"use strict"; return (' + expr + ");")();
    } catch (err) {
      return NaN;
    }
  }

  function computeTotal() {
    if (formulaCfg.type === "sum") {
      return inputsCfg.reduce(function (acc, inp) { return acc + scoreOf(inp.id); }, 0);
    }
    if (formulaCfg.type === "expression" && formulaCfg.expression) {
      var expr = formulaCfg.expression;
      inputsCfg.forEach(function (inp) {
        expr = expr.replace(new RegExp("\\b" + inp.id + "\\b", "g"), String(scoreOf(inp.id)));
      });
      var result = safeEval(expr);
      return isNaN(result) ? 0 : result;
    }
    return 0;
  }

  function findRange(total) {
    for (var i = 0; i < ranges.length; i += 1) {
      if (total >= ranges[i].min && total <= ranges[i].max) return ranges[i];
    }
    return null;
  }

  function fmt(n) {
    return decimals > 0 ? Number(n).toFixed(decimals) : String(Math.round(n));
  }

  function recommendationItems(range) {
    if (!range || !range.recommendations) return [];
    return range.recommendations.split("\n").map(function (line) {
      return line.replace(/^[•\-\s]+/, "").trim();
    }).filter(Boolean);
  }

  function revealClinical() {
    ["step-sae", "step-plan"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.hidden = false;
    });
  }

  function renderAll() {
    if (!inputsCfg.length) return;
    var total = computeTotal();
    var range = findRange(total);
    var valueEl = document.getElementById("calcResultValue");
    var unitEl = document.getElementById("calcResultUnit");
    var titleEl = document.getElementById("calcStatusTitle");
    var textEl = document.getElementById("calcStatusText");
    var block = document.getElementById("resultBlock");
    if (valueEl) valueEl.textContent = fmt(total);
    if (unitEl && formulaCfg.resultUnit) unitEl.textContent = formulaCfg.resultUnit;
    if (titleEl) titleEl.textContent = range ? range.label : "";
    if (textEl) textEl.textContent = range ? range.clinicalImplications : "";
    if (block && range && range.color) block.style.setProperty("--risk", range.color);

    var plan = document.getElementById("step-plan");
    if (plan) {
      var list = plan.querySelector(".action-list");
      var items = recommendationItems(range);
      if (list && items.length) {
        list.innerHTML = items.map(function (item) {
          return "<li>" + item.replace(/</g, "&lt;") + "</li>";
        }).join("");
      }
    }
  }

  function readField(el, inp) {
    var raw = el.value;
    state[inp.id] = inp.type === "number" ? parseFloat(raw) || 0 : raw;
  }

  inputsCfg.forEach(function (inp) {
    fields(inp.id).forEach(function (el) {
      ["input", "change"].forEach(function (evt) {
        el.addEventListener(evt, function () {
          readField(el, inp);
          renderAll();
        });
      });
    });
  });

  var form = document.getElementById("calcForm");
  if (form) {
    form.addEventListener("submit", function (evt) {
      evt.preventDefault();
      renderAll();
      revealClinical();
      var sae = document.getElementById("step-sae") || document.getElementById("step-plan");
      if (sae && sae.scrollIntoView) sae.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  document.querySelectorAll("[data-example]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var values;
      try {
        values = JSON.parse(btn.getAttribute("data-values") || "{}");
      } catch (err) {
        return;
      }
      Object.keys(values).forEach(function (key) {
        state[key] = values[key];
        fields(key).forEach(function (el) { el.value = String(values[key]); });
      });
      renderAll();
      revealClinical();
    });
  });

  document.querySelectorAll("[data-quiz-card]").forEach(function (card) {
    var correct = Number(card.getAttribute("data-correct"));
    card.querySelectorAll(".quiz-opt").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var chosen = Number(btn.getAttribute("data-opt"));
        card.querySelectorAll(".quiz-opt").forEach(function (opt) { opt.disabled = true; });
        btn.classList.add(chosen === correct ? "is-correct" : "is-wrong");
        var expl = card.querySelector(".quiz-expl");
        if (expl) expl.hidden = false;
      });
    });
  });

  renderAll();
})();
