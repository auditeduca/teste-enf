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
          renderAll();
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
     3b. Clinical Intelligence Package + Nurse-PaLM (preview_v2 / preview_apgar)
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

  function renderCIP(total, range) {
    var container = document.getElementById("cipContainer");
    if (!container) return;
    var severity = getRangeSeverity(range);
    var severityColor = { critical: "#dc2626", moderate: "#f59e0b", low: "#3b82f6", normal: "#2563eb", unknown: "#64748b" }[severity] || "#64748b";
    var severityLabel = { critical: "Crítico", moderate: "Moderado", low: "Baixo Risco", normal: "Normal", unknown: "—" }[severity] || "—";
    var html = "";
    var nandaList = sae.nanda || [];
    if (nandaList.length > 0) {
      html += '<div class="cip-dim cip-dim-nanda"><div class="cip-dim-header"><span class="cip-dim-icon">🔬</span><h4>Diagnósticos NANDA-I</h4>';
      html += '<span class="cip-dim-severity" style="background:' + severityColor + '20;color:' + severityColor + ';">' + severityLabel + "</span></div><div class=\"cip-dim-content\">";
      nandaList.forEach(function (n, i) {
        var dx = n.diagnosis || n.name || "";
        var def = n.definition || "";
        html += '<div class="cip-card"' + (i === 0 && severity !== "normal" ? ' style="border-color:' + severityColor + ';"' : "") + ">";
        html += '<div class="cip-card-title">' + dx + "</div>";
        if (def) html += '<div class="cip-card-desc">' + def.substring(0, 120) + (def.length > 120 ? "..." : "") + "</div>";
        html += "</div>";
      });
      html += "</div></div>";
    }
    var nicList = sae.nic || [];
    if (nicList.length > 0) {
      html += '<div class="cip-dim cip-dim-nic"><div class="cip-dim-header"><span class="cip-dim-icon">💊</span><h4>Intervenções NIC</h4></div><div class="cip-dim-content">';
      nicList.forEach(function (n) {
        var name = n.intervention || n.name || "";
        var activities = n.activities || [];
        html += '<div class="cip-card"><div class="cip-card-title">' + name + "</div>";
        if (activities.length) {
          html += "<ul class=\"cip-activities\">";
          activities.slice(0, 4).forEach(function (a) { html += "<li>" + a + "</li>"; });
          if (activities.length > 4) html += '<li class="cip-more">+' + (activities.length - 4) + " atividades</li>";
          html += "</ul>";
        }
        html += "</div>";
      });
      html += "</div></div>";
    }
    var nocList = sae.noc || [];
    if (nocList.length > 0) {
      html += '<div class="cip-dim cip-dim-noc"><div class="cip-dim-header"><span class="cip-dim-icon">🎯</span><h4>Outcomes NOC</h4></div><div class="cip-dim-content">';
      nocList.forEach(function (n) {
        var name = n.outcome || n.name || "";
        var indicators = n.indicators || [];
        html += '<div class="cip-card"><div class="cip-card-title">' + name + "</div>";
        if (indicators.length) {
          html += '<div class="cip-indicators">';
          indicators.slice(0, 3).forEach(function (ind) { html += '<span class="cip-indicator-tag">' + ind + "</span>"; });
          html += "</div>";
        }
        html += "</div>";
      });
      html += "</div></div>";
    }
    if (evidence.foundation || (evidence.references && evidence.references.length)) {
      html += '<div class="cip-dim cip-dim-evidence"><div class="cip-dim-header"><span class="cip-dim-icon">📚</span><h4>Evidência Científica</h4>';
      if (overview.evidenceLevel) html += '<span class="cip-dim-severity" style="background:#f59e0b20;color:#f59e0b;">Nível: ' + overview.evidenceLevel + "</span>";
      html += "</div><div class=\"cip-dim-content\">";
      if (evidence.foundation) html += '<div class="cip-card"><div class="cip-card-desc">' + evidence.foundation.substring(0, 200) + "...</div></div>";
      if (evidence.references && evidence.references.length) {
        html += '<div class="cip-references">';
        evidence.references.slice(0, 3).forEach(function (ref) {
          var refText = typeof ref === "string" ? ref : (ref.author || "") + " (" + (ref.year || "") + "). " + (ref.title || ref.text || "");
          html += '<div class="cip-reference">' + refText.substring(0, 100) + "</div>";
        });
        html += "</div>";
      }
      html += "</div></div>";
    }
    var safetyAlerts = [];
    if (severity === "critical") {
      safetyAlerts = ["IPSG-3: Segurança em procedimentos de alta vigilância", "Escalada de cuidado imediata — notificar equipe médica", "Documentação completa do evento em prontuário"];
    } else if (severity === "moderate") {
      safetyAlerts = ["Monitoramento contínuo recomendado", "Reavaliação em 15-30 minutos", "Verificar protocolo institucional correspondente"];
    } else if (severity === "normal") {
      safetyAlerts = ["Manter rotina de monitoramento padrão"];
    }
    if (safetyAlerts.length) {
      html += '<div class="cip-dim cip-dim-safety"><div class="cip-dim-header"><span class="cip-dim-icon">⚠️</span><h4>Metas de Segurança (IPSG)</h4></div><div class="cip-dim-content">';
      safetyAlerts.forEach(function (alert) {
        html += '<div class="cip-safety-alert" style="border-color:' + severityColor + ';">' + alert + "</div>";
      });
      html += "</div></div>";
    }
    var tips = learning.tips || [];
    if (tips.length) {
      html += '<div class="cip-dim cip-dim-learning"><div class="cip-dim-header"><span class="cip-dim-icon">🎓</span><h4>Dicas de Aprendizado</h4></div><div class="cip-dim-content">';
      tips.slice(0, 4).forEach(function (tip) { html += '<div class="cip-tip">💡 ' + tip + "</div>"; });
      html += "</div></div>";
    }
    if (!html) return;
    container.innerHTML = html;
    container.classList.remove("cip-hidden");
  }

  var cogTimer = null;
  function runCognitiveAnalysis(total, range) {
    if (cogTimer) clearTimeout(cogTimer);
    cogTimer = setTimeout(function () {
      var cogPanel = document.getElementById("cognitivePanel");
      if (!cogPanel || !window.NursePaLM || !window.CognitiveUI) return;
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
        return window.NursePaLM.NANDA_CPTS && Object.keys(window.NursePaLM.NANDA_CPTS).some(function (k) {
          return k.toLowerCase().indexOf(dx.substring(0, 5)) !== -1;
        });
      });
      var ctx = {
        observations: observations,
        activeDiagnoses: activeDx,
        episode_type: "assessment",
        tool_slug: TOOL_SLUG,
        tool_result: total,
        tool_range: range ? range.label : ""
      };
      var renderFn = window.CognitiveUI.renderCognitivePanel || window.CognitiveUI.render;
      if (!renderFn) return;
      Promise.resolve(renderFn(cogPanel, ctx)).then(function (result) {
        if (result && result.confidence != null) {
          var header = cogPanel.querySelector(".cognitive-panel-header h3");
          if (header) {
            var confPct = Math.round(result.confidence * 100);
            header.innerHTML = '<i class="fa-solid fa-brain"></i> Nurse-PaLM — ' + (range ? range.label : "Resultado") + " · Confiança: " + confPct + "%";
          }
        }
      }).catch(function (e) {
        console.error("[calc-engine-v2] Cognitive error:", e);
      });
      if (window.NursePaLM.TemporalGraph) {
        window.NursePaLM.TemporalGraph.record({ tool: TOOL_SLUG, result: total, range: range ? range.label : "", state: { result: total / 100 } });
      }
    }, 280);
  }

  function revealClinicalFlow(total, range) {
    var flowDivider = document.getElementById("calcFlowDivider");
    var clinicalFlow = document.getElementById("calcClinicalFlow");
    if (!clinicalFlow) return;
    var nandaText = document.getElementById("calcNandaText");
    var nicText = document.getElementById("calcNicText");
    var nocText = document.getElementById("calcNocText");
    var nanda = (sae.nanda && sae.nanda[0]) ? sae.nanda[0].diagnosis || sae.nanda[0].name : "";
    var nic = (sae.nic && sae.nic[0]) ? sae.nic[0].intervention || sae.nic[0].name : "";
    var noc = (sae.noc && sae.noc[0]) ? sae.noc[0].outcome || sae.noc[0].name : "";
    if (nandaText) nandaText.textContent = nanda || (range ? range.label : "—");
    if (nicText) nicText.textContent = nic || "Intervenções conforme protocolo institucional.";
    if (nocText) nocText.textContent = noc || "Monitorar evolução clínica e registrar no prontuário.";
    if (flowDivider) flowDivider.style.display = "block";
    clinicalFlow.classList.add("is-visible");
    window.requestAnimationFrame(function () {
      clinicalFlow.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  function triggerIntelligence(total, range) {
    renderCIP(total, range);
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
     5. Histórico (em memória — não usa localStorage, ver comentário no
        template original sobre consentimento de cookies)
  --------------------------------------------------------------------- */
  var history = [];
  function pushHistory(total, range) {
    history.unshift({ total: fmt(total), label: range ? range.label : "", time: new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) });
    history = history.slice(0, 5);
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
      favBtn.addEventListener("click", function () {
        var active = favBtn.classList.toggle("is-active");
        favBtn.setAttribute("aria-pressed", active ? "true" : "false");
        if (window.showToast) window.showToast(active ? "Adicionado aos favoritos" : "Removido dos favoritos");
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
    booted = true;
    initTabs();
    bindFields();
    bindExamples();
    initQuiz();
    initTimer();
    initActions();
    initForm();
    syncFieldsFromState();
    renderAll();
  }

  document.addEventListener("partials:ready", boot);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
