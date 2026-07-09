/* ==========================================================================
   js/calc-engine-v2.js — Motor genérico de calculadoras/escalas
   ==========================================================================
   Usado por toda página gerada a partir de data/tools/<slug>.json (ver
   tool.schema.json). A página já vem com o HTML/textos "assados" no server
   (gerados por scripts/generate_tool_page.py) para preservar SEO — este
   arquivo só cuida da parte INTERATIVA: reagir a mudanças nos campos,
   recalcular o resultado, sincronizar os painéis (Padrão/Estudante/Modo
   Urgência/Acadêmico) e o quiz.

   Contrato esperado no HTML da página:
   - <script type="application/json" id="tool-config">{...}</script>
     com o mesmo conteúdo do JSON em data/tools/<slug>.json.
   - Campos de entrada marcados com [data-calc-input="ID"] (select ou
     input[type=number]) — pode haver o MESMO id em vários painéis
     (padrao/estudante/urgencia); todos ficam sincronizados.
   - Célula de fórmula: [data-formula-box="ID"] e [data-formula-box="__result__"]
   - Banner de status: #calcStatusBanner / #calcStatusIcon / #calcStatusTitle / #calcStatusText
   - Resultado: #calcResultValue / #calcResultUnit
   - Painel Acadêmico > Cálculo: [data-aca-value="ID"] e [data-aca-value="__result__"]
   - Painel Estudante > passo-a-passo: [data-fd-step="ID"] e [data-fd-step="__result__"],
     badge de risco: #estFdBadge
   - Painel Urgência: #urgResultNum / #urgResultUnit / #urgAlarmBadge
   - Exemplos/presets: [data-example] com atributo data-values='{"id":valor,...}'
   - Histórico: #calcHistoryList / #calcHistoryEmpty (form#calcForm submit)
   - Ações: #calcFavoriteBtn / #calcShareBtn (impressão já usa onclick nativo)
   - Quiz: #estQuizCard com os sub-elementos já documentados abaixo
   ========================================================================== */
(function () {
  "use strict";

  /* ---------------------------------------------------------------------
     0. Config
  --------------------------------------------------------------------- */
  var configEl = document.getElementById("tool-config");
  if (!configEl) return; // página sem calculadora — nada a fazer
  var CONFIG;
  try {
    CONFIG = JSON.parse(configEl.textContent);
  } catch (e) {
    console.error("calc-engine-v2: JSON inválido em #tool-config", e);
    return;
  }

  var inputsCfg = (CONFIG.calculator && CONFIG.calculator.inputs) || [];
  var formulaCfg = (CONFIG.calculator && CONFIG.calculator.formula) || { type: "sum" };
  var ranges = (CONFIG.interpretation && CONFIG.interpretation.ranges) || [];
  var decimals = typeof formulaCfg.decimals === "number" ? formulaCfg.decimals : 0;
  var sae = CONFIG.sae || {};
  var evidence = CONFIG.evidence || {};
  var learning = CONFIG.learning || {};
  var overview = CONFIG.overview || {};
  var TOOL_SLUG = CONFIG.slug || "";

  /* ---------------------------------------------------------------------
     1. Abas genéricas (Padrão/Estudante/Urgência/Acadêmico/Gestor + sub-abas)
     Mesmo mecanismo já usado no resto do site (.tabs-inner/.tab/.tab-panel).
  --------------------------------------------------------------------- */
  function initTabs() {
    var groups = document.querySelectorAll("[data-tab-group]");
    groups.forEach(function (group) {
      var groupName = group.getAttribute("data-tab-group");
      var panelsWrap = document.querySelector('[data-tab-panels="' + groupName + '"]');
      if (!panelsWrap) return;
      group.querySelectorAll(".tab").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var target = btn.getAttribute("data-tab");
          group.querySelectorAll(".tab").forEach(function (b) {
            b.classList.toggle("active", b === btn);
            b.setAttribute("aria-selected", b === btn ? "true" : "false");
          });
          panelsWrap.querySelectorAll(":scope > [data-tab-panel]").forEach(function (p) {
            p.classList.toggle("active", p.getAttribute("data-tab-panel") === target);
          });
        });
      });
    });
  }

  /* ---------------------------------------------------------------------
     2. Estado + leitura/escrita de inputs (sincroniza cópias do mesmo id
        em painéis diferentes, sem sobrescrever campo em foco)
  --------------------------------------------------------------------- */
  var state = {};
  inputsCfg.forEach(function (inp) {
    state[inp.id] = inp.defaultValue !== undefined ? inp.defaultValue : (inp.options && inp.options[0] ? inp.options[0].value : 0);
  });

  function allFieldsFor(id) {
    return Array.prototype.slice.call(document.querySelectorAll('[data-calc-input="' + id + '"]'));
  }

  function setIfDifferent(el, value) {
    if (document.activeElement === el) return;
    var strVal = String(value);
    if (String(el.value) !== strVal) el.value = strVal;
  }

  function syncFieldsFromState() {
    inputsCfg.forEach(function (inp) {
      allFieldsFor(inp.id).forEach(function (el) {
        setIfDifferent(el, state[inp.id]);
      });
    });
  }

  function bindFields() {
    inputsCfg.forEach(function (inp) {
      allFieldsFor(inp.id).forEach(function (el) {
        el.addEventListener("input", function () {
          var raw = el.value;
          state[inp.id] = inp.type === "select" ? parseFloat(raw) : parseFloat(raw) || 0;
          syncFieldsFromState();
          renderAll();
        });
        el.addEventListener("change", function () {
          var raw = el.value;
          state[inp.id] = inp.type === "select" ? parseFloat(raw) : parseFloat(raw) || 0;
          syncFieldsFromState();
          var r = renderAll();
          if (!hasCalculated) revealClinicalFlow(r.total, r.range);
        });
      });
    });
  }

  /* ---------------------------------------------------------------------
     3. Cálculo
  --------------------------------------------------------------------- */
  function scoreOf(inputId) {
    var inp = inputsCfg.filter(function (i) { return i.id === inputId; })[0];
    if (!inp) return 0;
    var val = state[inputId];
    if (inp.type === "select" && inp.options) {
      var opt = inp.options.filter(function (o) { return Number(o.value) === Number(val); })[0];
      return opt ? Number(opt.score) : 0;
    }
    return Number(val) || 0;
  }

  // Avaliador aritmético restrito (apenas dígitos, + - * / ( ) . espaço) —
  // evita rodar qualquer coisa que não seja uma expressão numérica, mesmo
  // a expressão vindo do nosso próprio JSON (defesa em profundidade).
  function safeEval(expr) {
    if (!/^[0-9+\-*/().\s]+$/.test(expr)) return NaN;
    try {
      // eslint-disable-next-line no-new-func
      return Function('"use strict"; return (' + expr + ");")();
    } catch (e) {
      return NaN;
    }
  }

  function computeTotal() {
    if (formulaCfg.type === "sum") {
      var total = 0;
      inputsCfg.forEach(function (inp) { total += scoreOf(inp.id); });
      return total;
    }
    if (formulaCfg.type === "expression" && formulaCfg.expression) {
      var expr = formulaCfg.expression;
      inputsCfg.forEach(function (inp) {
        var re = new RegExp("\\b" + inp.id + "\\b", "g");
        expr = expr.replace(re, String(Number(state[inp.id]) || 0));
      });
      var result = safeEval(expr);
      return isNaN(result) ? 0 : result;
    }
    return 0;
  }

  function findRange(total) {
    for (var i = 0; i < ranges.length; i++) {
      var r = ranges[i];
      if (total >= r.min && total <= r.max) return r;
    }
    return null;
  }

  function fmt(n) {
    return decimals > 0 ? Number(n).toFixed(decimals) : String(Math.round(n));
  }

  function riskIsWarning(riskLevel) {
    return riskLevel === "high" || riskLevel === "critical";
  }

  /* ---------------------------------------------------------------------
     3b. Nurse-PaLM em background (preview_v2 — lógica integrada, sem painéis)
  --------------------------------------------------------------------- */
  var VITAL_MAP = {
    fc: "heartRate", frequencia_cardiaca: "heartRate", heart_rate: "heartRate", hr: "heartRate", pulso: "heartRate",
    pas: "systolicBP", pressao_sistolica: "systolicBP", systolic: "systolicBP", sbp: "systolicBP",
    pad: "diastolicBP", pressao_diastolica: "diastolicBP", diastolic: "diastolicBP",
    spo2: "spO2", saturacao: "spO2", sat: "spO2",
    fr: "respiratoryRate", frequencia_respiratoria: "respiratoryRate", respiratory_rate: "respiratoryRate",
    rr: "respiratoryRate", respiracao: "respiratoryRate",
    temp: "temperature", temperatura: "temperature",
    glasgow: "consciousness", consciencia: "consciousness",
    dor: "painScore", pain: "painScore", glicemia: "glucose", glicose: "glucose", glucose: "glucose"
  };

  function buildObservations(values) {
    var obs = [];
    Object.keys(values || {}).forEach(function (inpId) {
      var normalized = inpId.toLowerCase().replace(/[\s_\-]/g, "");
      var vitalType = VITAL_MAP[normalized] || VITAL_MAP[inpId.toLowerCase()];
      if (vitalType && values[inpId] > 0) {
        obs.push({ type: vitalType, value: values[inpId] });
      }
    });
    return obs;
  }

  function getRangeSeverity(range) {
    if (!range) return "unknown";
    var label = (range.label || "").toLowerCase();
    var color = range.color || "";
    if (color === "#dc2626" || color === "#b91c1c" || color === "#ef4444") return "critical";
    if (color === "#ea580c" || color === "#f59e0b" || color === "#f97316") return "moderate";
    if (color === "#2563eb" || color === "#3b82f6" || color === "#1d4ed8") return "normal";
    if (/grave|severo|crítico|critico|alto risco/.test(label)) return "critical";
    if (/moderado|moderada|médio|medio/.test(label)) return "moderate";
    if (/leve|baixo|baixa/.test(label)) return "low";
    if (/normal|bom|boa|preservado/.test(label)) return "normal";
    return range.riskLevel || "unknown";
  }

  function buildCIPHtml(total, range) {
    var severity = getRangeSeverity(range);
    var html = "";
    var ckoAi = (CONFIG._cko && CONFIG._cko.ai) || {};

    if (ckoAi.summary) {
      html += '<p class="flow-text cip-summary">' + ckoAi.summary + "</p>";
    }

    if (ckoAi.clinicalPearls && ckoAi.clinicalPearls.length) {
      html += '<div class="cip-dim cip-dim-pearls">';
      html += '<div class="cip-dim-header"><span class="cip-dim-icon">💡</span><h4>Pérolas clínicas</h4></div><div class="cip-dim-content">';
      ckoAi.clinicalPearls.forEach(function (tip) {
        html += '<div class="cip-tip">' + tip + "</div>";
      });
      html += "</div></div>";
    }

    if (ckoAi.commonErrors && ckoAi.commonErrors.length) {
      html += '<div class="cip-dim cip-dim-errors">';
      html += '<div class="cip-dim-header"><span class="cip-dim-icon">⚠️</span><h4>Erros comuns</h4></div><div class="cip-dim-content">';
      ckoAi.commonErrors.forEach(function (tip) {
        html += '<div class="cip-tip">' + tip + "</div>";
      });
      html += "</div></div>";
    }

    if (evidence.foundation || (evidence.references && evidence.references.length > 0)) {
      html += '<div class="cip-dim cip-dim-evidence" style="border-left: 4px solid #f59e0b;">';
      html += '<div class="cip-dim-header"><span class="cip-dim-icon">📚</span><h4>Evidência Científica</h4>';
      if (overview.evidenceLevel) html += '<span class="cip-dim-severity" style="background:#f59e0b20; color:#f59e0b;">Nível: ' + overview.evidenceLevel + "</span>";
      html += '</div><div class="cip-dim-content">';
      if (evidence.foundation) {
        html += '<div class="cip-card"><div class="cip-card-desc">' + evidence.foundation + "</div></div>";
      }
      if (evidence.limitations) {
        html += '<div class="cip-card"><div class="cip-card-desc"><strong>Limitações:</strong> ' + evidence.limitations + "</div></div>";
      }
      if (evidence.references && evidence.references.length > 0) {
        html += '<div class="cip-references">';
        evidence.references.slice(0, 3).forEach(function (ref) {
          var refText = typeof ref === "string" ? ref : (ref.text || (ref.author || "") + " (" + (ref.year || "") + "). " + (ref.title || ""));
          html += '<div class="cip-reference">' + refText + "</div>";
        });
        html += "</div>";
      }
      html += "</div></div>";
    }

    var tips = learning.tips || [];
    if (tips.length > 0) {
      html += '<div class="cip-dim cip-dim-learning" style="border-left: 4px solid #3b82f6;">';
      html += '<div class="cip-dim-header"><span class="cip-dim-icon">🎓</span><h4>Dicas de Aprendizado</h4></div><div class="cip-dim-content">';
      tips.slice(0, 4).forEach(function (tip) { html += '<div class="cip-tip">💡 ' + tip + "</div>"; });
      html += "</div></div>";
    }

    if (!html && severity !== "unknown") {
      html = '<p class="flow-text">Conteúdo de evidência carregado conforme o resultado do cálculo.</p>';
    }

    return html;
  }

  function renderCIP(total, range) {
    var html = buildCIPHtml(total, range);
    if (!html) return;
    var container = document.getElementById("cipContainer");
    if (!container) return;
    container.innerHTML = html;
    container.classList.remove("cip-hidden");
    container.style.display = "block";
    var cipCard = container.closest("[data-cip-section]");
    if (cipCard) cipCard.classList.remove("cip-hidden");
  }

  function showClinicalEngineSections() {
    document.querySelectorAll(
      "[data-cip-section], [data-kg-section], [data-cog-section]"
    ).forEach(function (el) {
      el.classList.remove("cip-hidden");
    });
  }

  function renderCognitiveResult(result, range) {
    if (!result || !window.CognitiveUI || !window.CognitiveUI.render) return;
    var panel = document.getElementById("cognitivePanel");
    if (!panel) return;
    panel.classList.remove("cip-hidden");
    var cogCard = panel.closest("[data-cog-section]");
    if (cogCard) cogCard.classList.remove("cip-hidden");
    var header = document.querySelector("#calcCogTitle");
    if (header && result.confidence != null) {
      var confPct = Math.round((result.confidence || 0) * 100);
      var engineLabel = result.source === "cir-edges" ? "CIR" : "Nurse-PaLM";
      header.innerHTML = '<svg class="icon icon-sm"><use href="#i-brain"/></svg> ' + engineLabel + " — " + (range ? range.label : "Resultado") + " · Confiança: " + confPct + "%";
    }
    window.CognitiveUI.render(panel, result);
  }

  function hideCipSections() {
    var cip = document.getElementById("cipContainer");
    if (cip) {
      cip.innerHTML = "";
      cip.classList.add("cip-hidden");
      cip.style.display = "none";
    }
    var cogPanel = document.getElementById("cognitivePanel");
    if (cogPanel) {
      cogPanel.classList.add("cip-hidden");
      var content = cogPanel.querySelector("#cognitivePanelContent, [data-cognitive-panel-content]");
      if (content) content.innerHTML = "";
    }
    document.querySelectorAll("[data-cip-section], [data-kg-section], [data-cog-section]").forEach(function (el) {
      el.classList.add("cip-hidden");
    });
  }

  var lastCognitiveResult = null;
  var cogTimer = null;
  var hasCalculated = false;

  var MEDICATION_TOOL_SLUGS = /gotejamento|insulina|medicamentos|dose|hora-extra|ferias|rescisao|adicional/i;
  var IPSG_BY_SEVERITY = {
    critical: ["Identificação correta do paciente", "Comunicação efetiva na transferência de cuidado", "Segurança em procedimentos de alta vigilância", "Notificar equipe e escalar cuidado"],
    moderate: ["Identificação correta do paciente", "Monitoramento contínuo conforme protocolo", "Comunicação SBAR em alterações"],
    low: ["Identificação correta do paciente", "Manter rotina de monitoramento"],
    normal: ["Identificação correta do paciente", "Documentação adequada no prontuário"],
    unknown: ["Identificação correta do paciente"]
  };
  var MEDS_NINE_RIGHTS = [
    "Paciente certo", "Medicamento certo", "Via certa", "Dose certa", "Hora certa",
    "Registro certo", "Ação certa", "Forma certa", "Resposta certa"
  ];
  var IPSG_FIEL_DEFAULT = [
    { tag: "M1", text: "Identificar o paciente corretamente" },
    { tag: "M2", text: "Melhorar a comunicação efetiva" },
    { tag: "M3", text: "Segurança na prescrição e administração" },
    { tag: "M5", text: "Higiene das mãos" },
    { tag: "M6", text: "Reduzir o risco de quedas" }
  ];
  var PRINT_CHECK_SVG = '<svg class="rr-list-item-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>';
  var PRINT_CHECK_BADGE_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>';
  var PRINT_WARN_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>';

  function isFielPrintTemplate() {
    var pt = document.getElementById("printTemplate");
    return !!(pt && pt.classList.contains("rr-fiel"));
  }

  function printRiskClass(range) {
    var sev = getRangeSeverity(range);
    if (sev === "critical" || sev === "high") return "rr-risk--critical";
    if (sev === "moderate") return "rr-risk--moderate";
    if (sev === "low" || sev === "normal") return "rr-risk--none";
    return "rr-risk--moderate";
  }

  function inputScoreMax(inp) {
    if (!inp.options || !inp.options.length) return null;
    var max = 0;
    inp.options.forEach(function (o) {
      var s = Number(o.score != null ? o.score : o.value);
      if (!isNaN(s) && s > max) max = s;
    });
    return max || null;
  }

  function computeScoreMax() {
    if (formulaCfg.scoreMax != null) return formulaCfg.scoreMax;
    if (ranges.length) {
      var hi = 0;
      ranges.forEach(function (r) { if (r.max != null && r.max > hi) hi = r.max; });
      if (hi) return hi;
    }
    if (formulaCfg.type === "sum") {
      var total = 0;
      inputsCfg.forEach(function (inp) { var m = inputScoreMax(inp); if (m) total += m; });
      return total || null;
    }
    return null;
  }

  function domText(id, fallback) {
    var el = document.getElementById(id);
    if (!el) return fallback != null ? fallback : "";
    var t = (el.textContent || "").replace(/\s+/g, " ").trim();
    if (!t || t === "—") return fallback != null ? fallback : "";
    return t;
  }

  function readToolHeaderFromDOM() {
    var header = document.querySelector(".tool-header");
    if (!header) return null;
    var h1 = header.querySelector("h1");
    var badge = header.querySelector(".tool-category-badge");
    return {
      name: h1 ? h1.textContent.trim() : "",
      category: badge ? badge.textContent.trim() : ""
    };
  }

  function readReferenceFromDOM() {
    var refLi = document.querySelector('[data-tab-panel="referencias"] .ref-list li, .ref-list li');
    if (!refLi) return "";
    var clone = refLi.cloneNode(true);
    var num = clone.querySelector(".ref-num");
    if (num) num.remove();
    return (clone.textContent || "").replace(/\s+/g, " ").trim();
  }

  function riskClassFromBanner() {
    var banner = document.getElementById("calcStatusBanner");
    if (!banner) return null;
    if (banner.classList.contains("danger") || banner.classList.contains("critical")) return "rr-risk--critical";
    if (banner.classList.contains("warning")) return "rr-risk--moderate";
    if (banner.classList.contains("success")) return "rr-risk--none";
    return null;
  }

  function buildPrintParamsFromDOM(fiel) {
    var form = document.getElementById("calcForm");
    if (!form) return null;
    var rows = [];
    form.querySelectorAll(".field-row").forEach(function (row) {
      var labelEl = row.querySelector(".field-label");
      var input = row.querySelector("[data-calc-input]");
      if (!labelEl || !input) return;
      var id = input.getAttribute("data-calc-input");
      var label = labelEl.textContent.trim();
      var scoreBox = document.querySelector('[data-formula-box="' + id + '"]');
      var inpCfg = inputsCfg.filter(function (i) { return i.id === id; })[0];
      var maxSc = inpCfg ? inputScoreMax(inpCfg) : null;
      var scoreTxt = "";
      if (fiel && scoreBox && maxSc != null) {
        scoreTxt = scoreBox.textContent.trim() + " / " + maxSc;
      }
      var display = scoreTxt;
      if (!display && input.tagName === "SELECT" && input.options.length) {
        display = input.options[input.selectedIndex].text.replace(/^\d+\s*—\s*/, "").trim();
        if (fiel && scoreBox) {
          display = scoreBox.textContent.trim() + (maxSc != null ? " / " + maxSc : "");
        }
      }
      if (!display) display = input.value;
      rows.push({ label: label, value: display });
    });
    return rows.length ? rows : null;
  }

  function ipsgTagForText(text, idx) {
    var match = IPSG_FIEL_DEFAULT.filter(function (item) {
      return text.indexOf(item.text) !== -1 || item.text.indexOf(text) !== -1;
    })[0];
    return match ? match.tag : "M" + (idx + 1);
  }

  function renderPrintIpsg(el) {
    if (!el) return;
    if (isFielPrintTemplate()) {
      var src = document.getElementById("calcSafetyIpsgList");
      var items = [];
      if (src && src.children.length) {
        items = Array.prototype.slice.call(src.querySelectorAll("li")).map(function (li) {
          return (li.textContent || "").replace(/\s+/g, " ").trim();
        }).filter(Boolean);
      }
      if (items.length) {
        el.innerHTML = items.map(function (text, idx) {
          return '<div class="rr-list-item"><span class="rr-list-item-tag">' + ipsgTagForText(text, idx) + '</span><span>' + text + "</span></div>";
        }).join("");
        return;
      }
      el.innerHTML = IPSG_FIEL_DEFAULT.map(function (item) {
        return '<div class="rr-list-item"><span class="rr-list-item-tag">' + item.tag + '</span><span>' + item.text + "</span></div>";
      }).join("");
      return;
    }
    var severity = "unknown";
    el.innerHTML = (IPSG_BY_SEVERITY[severity] || IPSG_BY_SEVERITY.unknown).map(function (t) {
      return "<li>" + t + "</li>";
    }).join("");
  }

  function renderPrintMeds(el, items) {
    if (!el) return;
    if (isFielPrintTemplate()) {
      var src = document.getElementById("calcSafetyMedsList");
      if ((!items || !items.length) && src && src.children.length) {
        items = Array.prototype.slice.call(src.querySelectorAll("li")).map(function (li) {
          return (li.textContent || "").replace(/\s+/g, " ").trim();
        }).filter(Boolean);
      }
    }
    if (!items || !items.length) return;
    if (isFielPrintTemplate()) {
      var half = Math.ceil(items.length / 2);
      var col1 = items.slice(0, half);
      var col2 = items.slice(half);
      function colHtml(list) {
        return list.map(function (t) {
          return '<div class="rr-list-item">' + PRINT_CHECK_SVG + "<span>" + t + "</span></div>";
        }).join("");
      }
      el.innerHTML = "<div>" + colHtml(col1) + "</div><div>" + colHtml(col2) + "</div>";
      return;
    }
    el.innerHTML = items.map(function (t) { return "<li>" + t + "</li>"; }).join("");
  }

  function buildCognitiveContext(total, range) {
    var observations = buildObservations(state);
    if (observations.length < 2) {
      var severity = getRangeSeverity(range);
      if (severity === "critical") {
        observations = [{ type: "heartRate", value: 120 }, { type: "systolicBP", value: 85 }, { type: "spO2", value: 88 }, { type: "respiratoryRate", value: 28 }];
      } else if (severity === "moderate") {
        observations = [{ type: "heartRate", value: 100 }, { type: "systolicBP", value: 100 }, { type: "spO2", value: 94 }, { type: "respiratoryRate", value: 20 }];
      } else {
        observations = [{ type: "heartRate", value: 75 }, { type: "systolicBP", value: 120 }, { type: "spO2", value: 98 }, { type: "respiratoryRate", value: 16 }];
      }
    }
    var activeDx = (sae.nanda || []).map(function (n) {
      return (n.diagnosis || n.name || "").toLowerCase().replace(/[^a-z]/g, "_");
    }).filter(function (dx) {
      return window.NursePaLM && window.NursePaLM.NANDA_CPTS && Object.keys(window.NursePaLM.NANDA_CPTS).some(function (k) {
        return k.toLowerCase().indexOf(dx.substring(0, 5)) !== -1;
      });
    });
    return {
      observations: observations,
      activeDiagnoses: activeDx,
      episode_type: "assessment",
      tool_slug: TOOL_SLUG,
      tool_result: total,
      tool_range: range ? range.label : ""
    };
  }

  function refreshConfigFromDom() {
    var el = document.getElementById("tool-config");
    if (!el) return;
    try {
      CONFIG = JSON.parse(el.textContent);
      sae = CONFIG.sae || sae;
      evidence = CONFIG.evidence || evidence;
      learning = CONFIG.learning || learning;
      overview = CONFIG.overview || overview;
    } catch (e) {
      console.warn("calc-engine-v2: não foi possível reler tool-config", e);
    }
  }

  function enrichSaeFromTerminology() {
    if (window.ClinicalTerminology && window.ClinicalTerminology.enrichSae) {
      var lang = document.documentElement.lang || "pt-BR";
      sae = window.ClinicalTerminology.enrichSae(sae, lang);
    }
  }

  function runEdgeInference(total) {
    var edges = window.ToolCKO && window.ToolCKO.edges;
    if (!edges || !window.CIRInference) return null;
    return window.CIRInference.infer(edges, total, {
      label: function (kind, code) {
        if (window.ClinicalTerminology && window.ClinicalTerminology.label) {
          return window.ClinicalTerminology.label(kind, code);
        }
        return "";
      },
    });
  }

  function syncSaeFromCirResult(result) {
    if (!result) return;
    if (result.diagnoses && result.diagnoses.length) {
      sae.nanda = result.diagnoses.map(function (d) {
        return {
          code: d.nanda_code || d.code,
          diagnosis: d.name,
          name: d.name,
          definition: (d.evidence || []).join("; "),
        };
      });
    }
    if (result.interventions && result.interventions.length) {
      sae.nic = result.interventions;
    }
    if (result.outcomes && result.outcomes.length) {
      sae.noc = result.outcomes;
    }
  }

  function pickNandaText(range) {
    if (lastCognitiveResult && lastCognitiveResult.diagnoses && lastCognitiveResult.diagnoses.length) {
      var dx = lastCognitiveResult.diagnoses[0];
      var label = dx.name || "";
      if (dx.probability) label += " (" + Math.round(dx.probability * 100) + "%)";
      return label;
    }
    var nanda = (sae.nanda && sae.nanda[0])
      ? sae.nanda[0].diagnosis || sae.nanda[0].name
      : "";
    if (!nanda && sae.nanda && sae.nanda[0] && sae.nanda[0].code && window.ClinicalTerminology) {
      nanda = window.ClinicalTerminology.label("nanda", sae.nanda[0].code);
    }
    return nanda || (range ? range.label : "—");
  }

  function pickNicText() {
    if (lastCognitiveResult && lastCognitiveResult.interventions && lastCognitiveResult.interventions.length) {
      var top = lastCognitiveResult.interventions[0];
      return top.name || top.intervention || "";
    }
    if (lastCognitiveResult && lastCognitiveResult.plan && lastCognitiveResult.plan.name) {
      return lastCognitiveResult.plan.name;
    }
    var nic = (sae.nic && sae.nic[0]) ? sae.nic[0].intervention || sae.nic[0].name : "";
    if (!nic && sae.nic && sae.nic[0] && sae.nic[0].code && window.ClinicalTerminology) {
      nic = window.ClinicalTerminology.label("nic", sae.nic[0].code);
    }
    return nic || "Intervenções conforme protocolo institucional.";
  }

  function pickNocText() {
    if (lastCognitiveResult && lastCognitiveResult.outcomes && lastCognitiveResult.outcomes.length) {
      var top = lastCognitiveResult.outcomes[0];
      return top.name || top.outcome || "";
    }
    var noc = (sae.noc && sae.noc[0]) ? sae.noc[0].outcome || sae.noc[0].name : "";
    if (!noc && sae.noc && sae.noc[0] && sae.noc[0].code && window.ClinicalTerminology) {
      noc = window.ClinicalTerminology.label("noc", sae.noc[0].code);
    }
    return noc || "Monitorar evolução clínica e registrar no prontuário.";
  }

  function applyClinicalFlowTexts(range) {
    var nanda = pickNandaText(range);
    var nic = pickNicText();
    var noc = pickNocText();
    var nandaText = document.getElementById("calcNandaText");
    var nicText = document.getElementById("calcNicText");
    var nocText = document.getElementById("calcNocText");
    if (nandaText) nandaText.textContent = nanda;
    if (nicText) nicText.textContent = nic;
    if (nocText) nocText.textContent = noc;
    document.querySelectorAll("[data-nnn-nanda]").forEach(function (el) { el.textContent = nanda; });
    document.querySelectorAll("[data-nnn-nic]").forEach(function (el) { el.textContent = nic; });
    document.querySelectorAll("[data-nnn-noc]").forEach(function (el) { el.textContent = noc; });
    applyConditionalSafety(range);
    applyCognitiveToProfiles(range);
    updateAcademicSaePanel(range);
  }

  function needsMedicationSafety() {
    if (CONFIG.calculator && CONFIG.calculator.involvesMedication) return true;
    return MEDICATION_TOOL_SLUGS.test(TOOL_SLUG) || MEDICATION_TOOL_SLUGS.test((overview.name || ""));
  }

  function applyConditionalSafety(range) {
    var severity = getRangeSeverity(range);
    var medsCol = document.getElementById("calcSafetyMeds");
    var ipsgCol = document.getElementById("calcSafetyIpsg");
    var medsList = document.getElementById("calcSafetyMedsList");
    var ipsgList = document.getElementById("calcSafetyIpsgList");
    var showMeds = needsMedicationSafety() || severity === "critical" || severity === "moderate";
    if (medsCol) medsCol.style.display = showMeds ? "" : "none";
    if (ipsgCol) ipsgCol.style.display = "";
    var ipsgItems = IPSG_BY_SEVERITY[severity] || IPSG_BY_SEVERITY.unknown;
    if (ipsgList) {
      ipsgList.innerHTML = ipsgItems.map(function (t) {
        return '<li><svg class="icon"><use href="#i-check"/></svg> ' + t + "</li>";
      }).join("");
    }
    if (medsList && showMeds) {
      var medCount = severity === "critical" ? 9 : (severity === "moderate" ? 7 : 5);
      medsList.innerHTML = MEDS_NINE_RIGHTS.slice(0, medCount).map(function (t) {
        return '<li><svg class="icon"><use href="#i-check"/></svg> ' + t + "</li>";
      }).join("");
    }
    var printMedsCol = document.getElementById("printSafetyMedsCol");
    var printMeds = document.getElementById("printSafetyMeds");
    var printIpsg = document.getElementById("printSafetyIpsg");
    if (printMedsCol) printMedsCol.hidden = !showMeds;
    if (printMedsCol) printMedsCol.style.display = showMeds ? "" : "none";
    if (printIpsg) renderPrintIpsg(printIpsg);
    if (printMeds && showMeds) renderPrintMeds(printMeds, MEDS_NINE_RIGHTS);
  }

  function applyCognitiveToProfiles(range) {
    var strip = document.getElementById("cognitiveProfileStrip");
    if (strip) {
      strip.classList.add("is-visible");
      var n = document.getElementById("cogStripNanda");
      var i = document.getElementById("cogStripNic");
      var o = document.getElementById("cogStripNoc");
      if (n) n.textContent = pickNandaText(range);
      if (i) i.textContent = pickNicText();
      if (o) o.textContent = pickNocText();
    }
    var urgHint = document.getElementById("urgCognitiveHint");
    if (urgHint) {
      urgHint.style.display = "block";
      urgHint.textContent = "Decisão clínica: " + pickNandaText(range) + " → " + pickNicText();
    }
    var estHint = document.getElementById("estCognitiveHint");
    if (estHint) {
      estHint.style.display = "block";
      estHint.textContent = "NOC esperado: " + pickNocText();
    }
    document.querySelectorAll('[data-tab-panel="sae"]').forEach(function (p) {
      p.classList.remove("cognitive-locked");
    });
  }

  function updateAcademicSaePanel(range) {
    var panel = document.querySelector('[data-tab-panel="sae"]');
    if (!panel || panel.classList.contains("cognitive-locked")) return;
    if (!hasCalculated) return;
    var html = "";
    var nandaList = (lastCognitiveResult && lastCognitiveResult.diagnoses && lastCognitiveResult.diagnoses.length)
      ? lastCognitiveResult.diagnoses.slice(0, 3).map(function (d) {
          return "<h4>NANDA — " + (d.name || "") + "</h4><p>Hipótese integrada pelo motor clínico (confiança " + Math.round((d.probability || 0) * 100) + "%).</p>";
        }).join("")
      : (sae.nanda || []).map(function (n) {
          return "<h4>NANDA — " + (n.diagnosis || n.name || "") + "</h4><p>" + (n.definition || "") + "</p>";
        }).join("");
    var nicList = (lastCognitiveResult && lastCognitiveResult.interventions && lastCognitiveResult.interventions.length)
      ? lastCognitiveResult.interventions.slice(0, 3).map(function (n) {
          var acts = (n.activities || []).slice(0, 4).map(function (a) { return "<li>" + a + "</li>"; }).join("");
          return "<h4>NIC — " + (n.intervention || n.name || "") + "</h4><ul class=\"tips-list\">" + acts + "</ul>";
        }).join("")
      : (sae.nic || []).map(function (n) {
      var acts = (n.activities || []).slice(0, 4).map(function (a) { return "<li>" + a + "</li>"; }).join("");
      return "<h4>NIC — " + (n.intervention || n.name || pickNicText()) + "</h4><ul class=\"tips-list\">" + acts + "</ul>";
        }).join("");
    var nocList = (lastCognitiveResult && lastCognitiveResult.outcomes && lastCognitiveResult.outcomes.length)
      ? lastCognitiveResult.outcomes.slice(0, 3).map(function (n) {
          var ind = (n.indicators || []).slice(0, 4).map(function (a) { return "<li>" + a + "</li>"; }).join("");
          return "<h4>NOC — " + (n.outcome || n.name || "") + "</h4><ul class=\"tips-list\">" + ind + "</ul>";
        }).join("")
      : (sae.noc || []).map(function (n) {
      var ind = (n.indicators || []).slice(0, 4).map(function (a) { return "<li>" + a + "</li>"; }).join("");
      return "<h4>NOC — " + (n.outcome || n.name || pickNocText()) + "</h4><ul class=\"tips-list\">" + ind + "</ul>";
    }).join("");
    html = nandaList + nicList + nocList;
    if (html) panel.innerHTML = html;
  }

  function hideClinicalUntilCalculated() {
    var flow = document.getElementById("calcClinicalFlow");
    var divider = document.getElementById("calcFlowDivider");
    if (flow) flow.classList.remove("is-visible");
    if (divider) divider.style.display = "none";
    document.querySelectorAll('[data-tab-panel="sae"]').forEach(function (p) {
      p.classList.add("cognitive-locked");
    });
    ["urgCognitiveHint", "estCognitiveHint"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.style.display = "none";
    });
    var strip = document.getElementById("cognitiveProfileStrip");
    if (strip) strip.classList.remove("is-visible");
    hideCipSections();
  }

  function runCognitiveAnalysis(total, range) {
    renderCIP(total, range);
    if (cogTimer) clearTimeout(cogTimer);
    cogTimer = setTimeout(function () {
      var pipeline = function (result) {
        lastCognitiveResult = result;
        if (result && result.source === "cir-edges") syncSaeFromCirResult(result);
        applyClinicalFlowTexts(range);
        renderCognitiveResult(result, range);
        showClinicalEngineSections();
      };

      var edgeResult = runEdgeInference(total);
      if (edgeResult && edgeResult.diagnoses && edgeResult.diagnoses.length) {
        pipeline(edgeResult);
        if (window.NursePaLM && window.NursePaLM.TemporalGraph) {
          window.NursePaLM.TemporalGraph.record({
            tool: TOOL_SLUG,
            result: total,
            range: range ? range.label : "",
            state: { result: total / 100, cir: "edges" },
          });
        }
        return;
      }

      var ctx = buildCognitiveContext(total, range);

      if (window.CognitiveUI && window.CognitiveUI.renderCognitivePanel) {
        showClinicalEngineSections();
        Promise.resolve(window.CognitiveUI.renderCognitivePanel("cognitivePanelContent", ctx)).then(pipeline).catch(function (e) {
          console.error("[calc-engine-v2] Cognitive UI error:", e);
        });
      } else if (window.NursePaLM && window.NursePaLM.runCognitivePipeline) {
        showClinicalEngineSections();
        Promise.resolve(window.NursePaLM.runCognitivePipeline(ctx)).then(pipeline).catch(function (e) {
          console.error("[calc-engine-v2] Cognitive error:", e);
        });
      }

      if (window.NursePaLM && window.NursePaLM.TemporalGraph) {
        window.NursePaLM.TemporalGraph.record({ tool: TOOL_SLUG, result: total, range: range ? range.label : "", state: { result: total / 100 } });
      }
    }, 280);
  }

  function revealClinicalFlow(total, range) {
    hasCalculated = true;
    var flowDivider = document.getElementById("calcFlowDivider");
    var clinicalFlow = document.getElementById("calcClinicalFlow");
    runCognitiveAnalysis(total, range);
    applyClinicalFlowTexts(range);
    showClinicalEngineSections();
    document.querySelectorAll(".cip-kg-links, [data-kg-section]").forEach(function (el) {
      el.classList.remove("cip-hidden");
    });
    if (flowDivider) flowDivider.style.display = "block";
    if (clinicalFlow) clinicalFlow.classList.add("is-visible");
    if (window.showToast) window.showToast("Motor clínico integrado disponível em todos os perfis", "success");
    var scrollTarget = clinicalFlow || document.getElementById("calcFlowDivider");
    if (scrollTarget) {
      window.requestAnimationFrame(function () {
        scrollTarget.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  }

  function triggerIntelligence(total, range) {
    if (!hasCalculated) return;
    runCognitiveAnalysis(total, range);
  }

  /* ---------------------------------------------------------------------
     4. Render — atualiza todos os painéis a partir do estado atual
  --------------------------------------------------------------------- */
  function renderAll() {
    var total = computeTotal();
    var range = findRange(total);
    var totalStr = fmt(total);

    // Padrão — resultado + banner
    var resVal = document.getElementById("calcResultValue");
    if (resVal) resVal.textContent = totalStr;
    var resUnit = document.getElementById("calcResultUnit");
    if (resUnit && formulaCfg.resultUnit) resUnit.textContent = formulaCfg.resultUnit;

    var banner = document.getElementById("calcStatusBanner");
    if (banner && range) {
      var warn = riskIsWarning(range.riskLevel);
      banner.classList.toggle("success", !warn);
      banner.classList.toggle("warning", warn);
      var icon = document.getElementById("calcStatusIcon");
      if (icon) icon.innerHTML = '<use href="#' + (warn ? "i-warning" : "i-check") + '"/>';
      var title = document.getElementById("calcStatusTitle");
      if (title) title.textContent = range.label;
      var text = document.getElementById("calcStatusText");
      if (text) text.textContent = range.clinicalImplications || "";
    }

    // Padrão — tira de fórmula
    inputsCfg.forEach(function (inp) {
      var box = document.querySelector('[data-formula-box="' + inp.id + '"]');
      if (box) box.textContent = formulaCfg.type === "sum" ? scoreOf(inp.id) : state[inp.id];
    });
    var resultBox = document.querySelector('[data-formula-box="__result__"]');
    if (resultBox) resultBox.textContent = totalStr;

    // Acadêmico > Cálculo
    inputsCfg.forEach(function (inp) {
      var el = document.querySelector('[data-aca-value="' + inp.id + '"]');
      if (!el) return;
      if (inp.type === "select" && inp.options) {
        var opt = inp.options.filter(function (o) { return Number(o.value) === Number(state[inp.id]); })[0];
        el.textContent = opt ? opt.label + " (" + opt.score + ")" : "";
      } else {
        el.textContent = state[inp.id];
      }
    });
    var acaResult = document.querySelector('[data-aca-value="__result__"]');
    if (acaResult) acaResult.textContent = totalStr + (formulaCfg.resultUnit ? " " + formulaCfg.resultUnit : "");
    var acaRange = document.querySelector('[data-aca-value="__range__"]');
    if (acaRange && range) acaRange.textContent = range.label;

    // Estudante — passo a passo (formula-dark)
    inputsCfg.forEach(function (inp) {
      var step = document.querySelector('[data-fd-step="' + inp.id + '"]');
      if (step) step.textContent = formulaCfg.type === "sum" ? scoreOf(inp.id) : state[inp.id];
    });
    var fdResult = document.querySelector('[data-fd-step="__result__"]');
    if (fdResult) fdResult.textContent = totalStr;
    var fdBadge = document.getElementById("estFdBadge");
    if (fdBadge && range) {
      var warnBadge = riskIsWarning(range.riskLevel);
      fdBadge.classList.toggle("alarm", warnBadge);
      fdBadge.innerHTML = '<svg class="icon icon-sm"><use href="#' + (warnBadge ? "i-warning" : "i-check") + '"/></svg> ' + range.label;
    }

    // Modo Urgência
    var urgNum = document.getElementById("urgResultNum");
    if (urgNum) {
      urgNum.textContent = totalStr;
      var warnUrg = range ? riskIsWarning(range.riskLevel) : false;
      urgNum.classList.toggle("alarm", warnUrg);
      urgNum.classList.toggle("safe", !warnUrg);
    }
    var urgUnit = document.getElementById("urgResultUnit");
    if (urgUnit && formulaCfg.resultUnit) urgUnit.textContent = formulaCfg.resultUnit;
    var urgBadge = document.getElementById("urgAlarmBadge");
    if (urgBadge && range) {
      var warnUrgBadge = riskIsWarning(range.riskLevel);
      urgBadge.classList.toggle("alarm", warnUrgBadge);
      urgBadge.classList.toggle("safe", !warnUrgBadge);
      urgBadge.innerHTML = '<svg class="icon icon-sm"><use href="#' + (warnUrgBadge ? "i-warning" : "i-check") + '"/></svg> ' + range.label;
    }

    triggerIntelligence(total, range);
    return { total: total, range: range };
  }

  /* ---------------------------------------------------------------------
     4b. Impressão — relatório padrão (relatorio.pdf / print-template.css)
  --------------------------------------------------------------------- */
  function formatReference(ref) {
    if (!ref) return "Documento gerado automaticamente.";
    if (typeof ref === "string") return ref;
    if (ref.text) return ref.text;
    return ((ref.author || "") + " (" + (ref.year || "") + "). " + (ref.title || "")).trim();
  }

  function populatePrintReport(total, range) {
    var pt = document.getElementById("printTemplate");
    if (!pt) return;
    var fiel = isFielPrintTemplate();
    var headerDom = readToolHeaderFromDOM();
    var acronym = overview.acronym ? overview.acronym + " — " : "";
    var name = (headerDom && headerDom.name) || (acronym + (overview.name || document.title));
    var catBase = (headerDom && headerDom.category) || overview.categoryBadge || (CONFIG.breadcrumb && CONFIG.breadcrumb.category) || "Escala clínica";
    var catExtra = overview.specialty && overview.specialty[0] ? " • " + overview.specialty[0] : "";
    var cat = catBase + catExtra;
    var el;
    el = document.getElementById("printToolName"); if (el) el.textContent = name;
    el = document.getElementById("printToolCategory"); if (el) el.textContent = cat;
    var toolIcon = document.querySelector(".tool-header .tool-icon-badge svg");
    var printIcon = document.getElementById("printToolIcon");
    if (printIcon && toolIcon) printIcon.innerHTML = toolIcon.innerHTML;
    el = document.getElementById("printDate");
    if (el) {
      var now = new Date();
      var sep = fiel ? " • " : " — ";
      el.textContent = now.toLocaleDateString("pt-BR") + sep + now.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    }
    try {
      var ctx = JSON.parse(localStorage.getItem("patientContext") || "{}");
      el = document.getElementById("printPatientName"); if (el) el.textContent = ctx.name || "—";
      el = document.getElementById("printPatientReg"); if (el) el.textContent = ctx.reg || "—";
      el = document.getElementById("printPatientAge"); if (el) el.textContent = ctx.age || "—";
      el = document.getElementById("printPatientBed"); if (el) el.textContent = ctx.bed || "—";
    } catch (e) { /* ignore */ }
    var paramsList = document.getElementById("printParamsList");
    if (paramsList) {
      paramsList.innerHTML = "";
      var domParams = buildPrintParamsFromDOM(fiel);
      var paramRows = domParams || inputsCfg.map(function (inp) {
        var val = state[inp.id];
        var label = inp.label || inp.id;
        var scoreTxt = "";
        if (inp.type === "select" && inp.options) {
          var opt = inp.options.filter(function (o) { return Number(o.value) === Number(val); })[0];
          var maxSc = inputScoreMax(inp);
          if (fiel && formulaCfg.type === "sum" && maxSc != null) {
            scoreTxt = scoreOf(inp.id) + " / " + maxSc;
          } else if (opt) {
            val = opt.label;
            if (fiel && maxSc != null && formulaCfg.type === "sum") scoreTxt = scoreOf(inp.id) + " / " + maxSc;
          }
        }
        return { label: label, value: scoreTxt || val };
      });
      paramRows.forEach(function (row) {
        if (fiel) {
          var div = document.createElement("div");
          div.className = "rr-parameter-item";
          div.innerHTML = "<div>" + row.label + '</div><div class="rr-parameter-score">' + row.value + "</div>";
          paramsList.appendChild(div);
        } else {
          var li = document.createElement("li");
          li.innerHTML = '<span class="param-label">' + row.label + '</span><span class="param-value">' + row.value + "</span>";
          paramsList.appendChild(li);
        }
      });
    }
    var riskCls = riskClassFromBanner() || printRiskClass(range);
    var resultCard = document.getElementById("printResultCard");
    if (resultCard) {
      resultCard.className = "rr-result-card " + riskCls;
    }
    var scoreDom = domText("calcResultValue", fmt(total));
    el = document.getElementById("printScore");
    if (el) el.textContent = scoreDom;
    el = document.getElementById("printScoreMax");
    if (el) {
      var maxScore = computeScoreMax();
      var unitDom = domText("calcResultUnit", formulaCfg.resultUnit || "pontos");
      el.textContent = maxScore ? "de " + maxScore + " " + unitDom : unitDom;
    }
    var classLabel = domText("calcStatusTitle", range ? range.label : "—");
    el = document.getElementById("printClassification");
    if (el) {
      el.className = fiel ? "rr-classification-badge " + riskCls : "label";
      var warn = range && riskIsWarning(range.riskLevel);
      if (fiel) {
        el.innerHTML = (warn ? PRINT_WARN_SVG : PRINT_CHECK_BADGE_SVG) + " " + classLabel;
      } else {
        el.textContent = classLabel;
      }
    }
    el = document.getElementById("printInterpretation");
    if (el) el.textContent = domText("calcStatusText", range ? (range.clinicalImplications || "") : "");
    var nandaSection = document.getElementById("printNandaSection");
    var flow = document.getElementById("calcClinicalFlow");
    var nandaDom = domText("calcNandaText");
    var hasSae = !!(flow && flow.classList.contains("is-visible") && nandaDom) ||
      (sae.nanda && sae.nanda.length) || (sae.nic && sae.nic.length) || (sae.noc && sae.noc.length);
    if (nandaSection) nandaSection.hidden = !hasSae;
    el = document.getElementById("printNandaText"); if (el) el.textContent = nandaDom || pickNandaText(range);
    el = document.getElementById("printNicText"); if (el) el.textContent = domText("calcNicText", pickNicText());
    el = document.getElementById("printNocText"); if (el) el.textContent = domText("calcNocText", pickNocText());
    el = document.getElementById("printReference");
    if (el) {
      var refDom = readReferenceFromDOM();
      if (refDom) el.textContent = refDom;
      else if (evidence.references && evidence.references[0]) el.textContent = formatReference(evidence.references[0]);
      else el.textContent = "Documento gerado automaticamente.";
    }
    applyConditionalSafety(range);
  }

  var printTitleBackup = null;

  function openPrintOrApi() {
    var r = renderAll();
    populatePrintReport(r.total, r.range);
    var apiBase = document.body && document.body.getAttribute("data-report-api");
    if (apiBase && window.ReportPayload && window.ReportPayload.generateViaApi) {
      return window.ReportPayload.generateViaApi(apiBase).catch(function (err) {
        console.warn("[calc-engine] API de relatório indisponível, usando window.print", err);
        printTitleBackup = document.title;
        document.title = "relatorio";
        window.print();
      });
    }
    printTitleBackup = document.title;
    document.title = "relatorio";
    window.print();
  }

  function initPrint() {
    var printBtn = document.getElementById("calcPrintBtn");
    if (printBtn) {
      printBtn.removeAttribute("onclick");
      printBtn.addEventListener("click", function (e) {
        e.preventDefault();
        if (!hasCalculated) {
          if (window.showToast) window.showToast("Calcule antes de imprimir o relatório", "info");
          return;
        }
        if (!document.getElementById("printTemplate")) {
          if (window.showToast) window.showToast("Aguarde o carregamento do relatório", "info");
          return;
        }
        openPrintOrApi();
      });
    }
    document.querySelectorAll(".aca-print-btn").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        if (!hasCalculated) {
          e.preventDefault();
          if (window.showToast) window.showToast("Calcule antes de exportar", "info");
          return;
        }
        var r = renderAll();
        populatePrintReport(r.total, r.range);
      });
    });
    window.addEventListener("beforeprint", function () {
      var pt = document.getElementById("printTemplate");
      if (!pt || !hasCalculated) return;
      var r = renderAll();
      populatePrintReport(r.total, r.range);
      pt.style.display = "block";
      pt.classList.remove("no-print-screen");
      if (!printTitleBackup) printTitleBackup = document.title;
      document.title = "relatorio";
    });
    window.addEventListener("afterprint", function () {
      var pt = document.getElementById("printTemplate");
      if (pt) { pt.style.display = "none"; pt.classList.add("no-print-screen"); }
      if (printTitleBackup) {
        document.title = printTitleBackup;
        printTitleBackup = null;
      }
    });
  }

  /* ---------------------------------------------------------------------
     5. Histórico (em memória — não usa localStorage, ver comentário no
        template original sobre consentimento de cookies)
  --------------------------------------------------------------------- */
  function historyStorageKey() {
    return "calc-history-" + (TOOL_SLUG || "tool");
  }

  function favoritesStorageKey() {
    return "tool-favorites";
  }

  function loadHistoryFromStorage() {
    try {
      var raw = localStorage.getItem(historyStorageKey());
      if (!raw) return [];
      var list = JSON.parse(raw);
      return Array.isArray(list) ? list : [];
    } catch (e) {
      return [];
    }
  }

  function saveHistoryToStorage() {
    try {
      localStorage.setItem(historyStorageKey(), JSON.stringify(history));
    } catch (e) { /* quota */ }
  }

  function isFavoriteTool() {
    try {
      var list = JSON.parse(localStorage.getItem(favoritesStorageKey()) || "[]");
      return list.indexOf(TOOL_SLUG) !== -1;
    } catch (e) {
      return false;
    }
  }

  function setFavoriteTool(active) {
    try {
      var list = JSON.parse(localStorage.getItem(favoritesStorageKey()) || "[]");
      var idx = list.indexOf(TOOL_SLUG);
      if (active && idx === -1) list.push(TOOL_SLUG);
      if (!active && idx !== -1) list.splice(idx, 1);
      localStorage.setItem(favoritesStorageKey(), JSON.stringify(list));
    } catch (e) { /* ignore */ }
  }

  var history = loadHistoryFromStorage();
  function pushHistory(total, range) {
    history.unshift({ total: fmt(total), label: range ? range.label : "", time: new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) });
    history = history.slice(0, 5);
    saveHistoryToStorage();
    renderHistory();
  }
  function renderHistory() {
    var list = document.getElementById("calcHistoryList");
    if (!list) return;
    if (!history.length) {
      list.innerHTML = '<li class="history-empty" id="calcHistoryEmpty">Seus últimos cálculos aparecerão aqui nesta sessão.</li>';
      return;
    }
    list.innerHTML = history.map(function (h) {
      return '<li class="history-item"><span><span class="h-result">' + h.total + (formulaCfg.resultUnit ? " " + formulaCfg.resultUnit : "") + '</span><br><span class="h-meta">' + h.label + " · " + h.time + '</span></span></li>';
    }).join("");
  }

  /* ---------------------------------------------------------------------
     6. Exemplos / presets (Estudante e Modo Urgência)
  --------------------------------------------------------------------- */
  function bindExamples() {
    document.querySelectorAll("[data-example]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var raw = btn.getAttribute("data-values");
        if (!raw) return;
        try {
          var values = JSON.parse(raw);
          Object.keys(values).forEach(function (k) { state[k] = values[k]; });
          syncFieldsFromState();
          renderAll();
        } catch (e) { /* ignore */ }
      });
    });
  }

  /* ---------------------------------------------------------------------
     7. Quiz genérico
  --------------------------------------------------------------------- */
  function initQuiz() {
    var quiz = (CONFIG.learning && CONFIG.learning.quiz) || [];
    var card = document.getElementById("estQuizCard");
    if (!card || !quiz.length) return;

    var idx = 0, picked = null;
    var qEl = document.getElementById("estQuizQuestion");
    var optsEl = document.getElementById("estQuizOpts");
    var explEl = document.getElementById("estQuizExpl");
    var nextBtn = document.getElementById("estQuizNext");
    var progEl = document.getElementById("estQuizProgress");

    function render() {
      var item = quiz[idx];
      if (progEl) progEl.textContent = (idx + 1) + "/" + quiz.length;
      if (qEl) qEl.textContent = item.q;
      if (explEl) explEl.innerHTML = "";
      if (nextBtn) nextBtn.style.display = "none";
      if (optsEl) {
        optsEl.innerHTML = item.opts.map(function (opt, i) {
          return '<li><button type="button" class="quiz-opt" data-i="' + i + '">' + opt + "</button></li>";
        }).join("");
        optsEl.querySelectorAll(".quiz-opt").forEach(function (btn) {
          btn.addEventListener("click", function () { pick(Number(btn.getAttribute("data-i"))); });
        });
      }
    }
    function pick(i) {
      if (picked !== null) return;
      picked = i;
      var item = quiz[idx];
      optsEl.querySelectorAll(".quiz-opt").forEach(function (btn, bi) {
        btn.disabled = true;
        if (bi === item.correct) btn.classList.add("correct");
        else if (bi === i) btn.classList.add("wrong");
        else btn.classList.add("dim");
      });
      var ok = i === item.correct;
      explEl.innerHTML = '<div class="' + (ok ? "correct" : "wrong") + '">' + (ok ? "✔ Correto! " : "✘ Não foi dessa vez. ") + (item.expl || "") + "</div>";
      if (nextBtn) nextBtn.style.display = idx < quiz.length - 1 ? "flex" : "none";
    }
    if (nextBtn) {
      nextBtn.addEventListener("click", function () {
        idx = (idx + 1) % quiz.length;
        picked = null;
        render();
      });
    }
    render();
  }

  /* ---------------------------------------------------------------------
     8. Cronômetro de infusão (só quando o schema pedir, ex: calculadoras
        de gotejamento) — opcional, ligado por CONFIG.calculator.showTimer.
  --------------------------------------------------------------------- */
  function initTimer() {
    if (!CONFIG.calculator || !CONFIG.calculator.showTimer) return;
    var btn = document.getElementById("urgTimerBtn");
    var numEl = document.getElementById("urgTimerNum");
    if (!btn || !numEl) return;
    var running = false, seconds = 0, timer = null;
    function tick() {
      seconds++;
      var h = String(Math.floor(seconds / 3600)).padStart(2, "0");
      var m = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
      var s = String(seconds % 60).padStart(2, "0");
      numEl.textContent = h + ":" + m + ":" + s;
    }
    btn.addEventListener("click", function () {
      running = !running;
      if (running) {
        btn.classList.remove("start"); btn.classList.add("stop");
        btn.innerHTML = '<svg class="icon icon-sm"><use href="#i-warning"/></svg> Parar infusão';
        timer = setInterval(tick, 1000);
      } else {
        btn.classList.remove("stop"); btn.classList.add("start");
        btn.innerHTML = '<svg class="icon icon-sm"><use href="#i-play"/></svg> Iniciar infusão';
        clearInterval(timer);
      }
    });
  }

  /* ---------------------------------------------------------------------
     9. Ações (Favoritar / Compartilhar) — Imprimir já usa onclick nativo
  --------------------------------------------------------------------- */
  function initActions() {
    var favBtn = document.getElementById("calcFavoriteBtn");
    if (favBtn) {
      if (isFavoriteTool()) {
        favBtn.classList.add("is-active");
        favBtn.setAttribute("aria-pressed", "true");
      }
      favBtn.addEventListener("click", function () {
        var active = favBtn.classList.toggle("is-active");
        favBtn.setAttribute("aria-pressed", active ? "true" : "false");
        setFavoriteTool(active);
        if (window.showToast) window.showToast(active ? "Adicionado aos favoritos (salvo no navegador)" : "Removido dos favoritos");
      });
    }
    var shareBtn = document.getElementById("calcShareBtn");
    if (shareBtn) {
      shareBtn.addEventListener("click", function () {
        var url = window.location.href;
        var title = CONFIG.overview ? CONFIG.overview.name : document.title;
        if (navigator.share) {
          navigator.share({ title: title, url: url }).catch(function () {});
        } else if (navigator.clipboard) {
          navigator.clipboard.writeText(url).then(function () {
            if (window.showToast) window.showToast("Link copiado para a área de transferência");
          });
        }
      });
    }
  }

  /* ---------------------------------------------------------------------
     10. Envio do formulário Padrão -> histórico
  --------------------------------------------------------------------- */
  function initForm() {
    var form = document.getElementById("calcForm");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var r = renderAll();
      pushHistory(r.total, r.range);
      revealClinicalFlow(r.total, r.range);
    });
    form.addEventListener("reset", function () {
      hasCalculated = false;
      lastCognitiveResult = null;
      hideClinicalUntilCalculated();
      setTimeout(function () {
        inputsCfg.forEach(function (inp) {
          state[inp.id] = inp.defaultValue !== undefined ? inp.defaultValue : (inp.options && inp.options[0] ? inp.options[0].value : 0);
        });
        syncFieldsFromState();
        renderAll();
      }, 0);
    });
  }

  /* ---------------------------------------------------------------------
     Boot
  --------------------------------------------------------------------- */
  var booted = false;
  function boot() {
    if (booted) return;
    if (document.getElementById("printTemplateMount") && !document.getElementById("printTemplate")) return;
    booted = true;
    refreshConfigFromDom();
    enrichSaeFromTerminology();
    initTabs();
    bindFields();
    bindExamples();
    initQuiz();
    initTimer();
    initActions();
    initPrint();
    initForm();
    hideClinicalUntilCalculated();
    syncFieldsFromState();
    renderHistory();
    renderAll();
  }

  document.addEventListener("partials:ready", boot);
  document.addEventListener("print-template:ready", boot);
  document.addEventListener("tool-profile:ready", function () {
    if (!hasCalculated) return;
    var r = renderAll();
    renderCIP(r.total, r.range);
    applyClinicalFlowTexts(r.range);
    if (lastCognitiveResult) renderCognitiveResult(lastCognitiveResult, r.range);
    showClinicalEngineSections();
    var flow = document.getElementById("calcClinicalFlow");
    var divider = document.getElementById("calcFlowDivider");
    if (flow) flow.classList.add("is-visible");
    if (divider) divider.style.display = "block";
  });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
