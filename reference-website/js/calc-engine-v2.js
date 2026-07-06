/* ==========================================================================
   js/calc-engine-v2.js — Motor de Calculadoras com Nurse-PaLM Integrado
   ==========================================================================
   Substitui calc-engine.js. Diferenças:
   1. Após calcular o resultado, dispara automaticamente o Nurse-PaLM
   2. Mostra inline as 6 dimensões do Clinical Intelligence Package:
      - NANDA diagnósticos associados à faixa de resultado
      - NIC intervenções recomendadas
      - NOC outcomes esperados
      - Evidência científica
      - Metas de segurança
      - Dicas de aprendizado
   3. Painel cognitivo com raciocínio bayesiano em tempo real
   4. Biblioteca de recursos conectada ao resultado
   ========================================================================== */
(function () {
  "use strict";

  /* ---------------------------------------------------------------------
     0. Config — load tool data
  --------------------------------------------------------------------- */
  var configEl = document.getElementById("tool-config");
  if (!configEl) return;
  var CONFIG;
  try {
    CONFIG = JSON.parse(configEl.textContent);
  } catch (e) {
    console.error("calc-engine-v2: JSON inválido", e);
    return;
  }

  var TOOL_SLUG = CONFIG.slug || "";
  var inputsCfg = (CONFIG.calculator && CONFIG.calculator.inputs) || [];
  var formulaCfg = (CONFIG.calculator && CONFIG.calculator.formula) || { type: "sum" };
  var ranges = (CONFIG.interpretation && CONFIG.interpretation.ranges) || [];
  var decimals = typeof formulaCfg.decimals === "number" ? formulaCfg.decimals : 0;
  var sae = CONFIG.sae || {};
  var evidence = CONFIG.evidence || {};
  var learning = CONFIG.learning || {};
  var faq = CONFIG.faq || [];
  var overview = CONFIG.overview || {};

  /* ---------------------------------------------------------------------
     1. Calculation Engine (preserved from v1)
  --------------------------------------------------------------------- */
  function getInputs(panel) {
    panel = panel || document;
    var values = {};
    inputsCfg.forEach(function (inp) {
      var el = panel.querySelector('[data-calc-input="' + inp.id + '"]');
      if (el) {
        var v = parseFloat(el.value);
        values[inp.id] = isNaN(v) ? 0 : v;
      }
    });
    return values;
  }

  function computeResult(values) {
    if (formulaCfg.type === "sum") {
      var sum = 0;
      for (var k in values) sum += values[k];
      return sum;
    } else if (formulaCfg.type === "avg") {
      var s = 0, c = 0;
      for (var k in values) { s += values[k]; c++; }
      return c > 0 ? s / c : 0;
    } else if (formulaCfg.type === "max") {
      var mx = -Infinity;
      for (var k in values) if (values[k] > mx) mx = values[k];
      return mx === -Infinity ? 0 : mx;
    } else if (formulaCfg.type === "formula" && formulaCfg.expr) {
      try {
        var expr = formulaCfg.expr;
        for (var k in values) {
          expr = expr.replace(new RegExp("\\b" + k + "\\b", "g"), values[k]);
        }
        return eval(expr);
      } catch (e) {
        return 0;
      }
    }
    return 0;
  }

  function findRange(result) {
    for (var i = 0; i < ranges.length; i++) {
      var r = ranges[i];
      if (result >= (r.min || 0) && result <= (r.max || Infinity)) {
        return r;
      }
    }
    return ranges[0] || null;
  }

  /* ---------------------------------------------------------------------
     2. Nurse-PaLM Integration — Auto-trigger after calculation
  --------------------------------------------------------------------- */

  // Vital sign mapping (tool input → Nurse-PaLM observation type)
  var VITAL_MAP = {
    'fc': 'heartRate', 'frequencia_cardiaca': 'heartRate', 'frequênciacardíaca': 'heartRate', 'heart_rate': 'heartRate', 'hr': 'heartRate', 'pulso': 'heartRate',
    'pas': 'systolicBP', 'pressao_sistolica': 'systolicBP', 'pressãosistolica': 'systolicBP', 'systolic': 'systolicBP', 'sbp': 'systolicBP', 'sistolica': 'systolicBP',
    'pad': 'diastolicBP', 'pressao_diastolica': 'diastolicBP', 'diastolic': 'diastolicBP',
    'spo2': 'spO2', 'saturacao': 'spO2', 'saturação': 'spO2', 'sat': 'spO2',
    'fr': 'respiratoryRate', 'frequencia_respiratoria': 'respiratoryRate', 'frequênciarespiratória': 'respiratoryRate', 'respiratory_rate': 'respiratoryRate', 'rr': 'respiratoryRate', 'respiracao': 'respiratoryRate', 'respiração': 'respiratoryRate',
    'temp': 'temperature', 'temperatura': 'temperature', 'axilar': 'temperature',
    'diurese': 'urineOutput', 'urine': 'urineOutput', 'debito': 'urineOutput', 'débito': 'urineOutput',
    'glasgow': 'consciousness', 'consciencia': 'consciousness', 'consciência': 'consciousness',
    'dor': 'painScore', 'pain': 'painScore', 'escala_numerica': 'painScore', 'escalanumerica': 'painScore',
    'glicemia': 'glucose', 'glicose': 'glucose', 'glucose': 'glucose'
  };

  function buildObservations(values) {
    var obs = [];
    for (var inpId in values) {
      var normalized = inpId.toLowerCase().replace(/[\s_\-]/g, '');
      var vitalType = VITAL_MAP[normalized] || VITAL_MAP[inpId.toLowerCase()];
      if (vitalType && values[inpId] > 0) {
        obs.push({ type: vitalType, value: values[inpId] });
      }
    }
    return obs;
  }

  function getCurrentRange() {
    var resultEl = document.getElementById("calcResultValue");
    if (!resultEl) return null;
    var result = parseFloat(resultEl.textContent) || 0;
    return findRange(result);
  }

  function getRangeSeverity(range) {
    if (!range) return 'unknown';
    var label = (range.label || '').toLowerCase();
    var color = range.color || '';
    if (color === '#dc2626' || color === '#b91c1c' || color === '#ef4444') return 'critical';
    if (color === '#ea580c' || color === '#f59e0b' || color === '#f97316') return 'moderate';
    if (color === '#2563eb' || color === '#3b82f6' || color === '#1d4ed8') return 'normal';
    if (/grave|severo|crítico|critico|alto risco/.test(label)) return 'critical';
    if (/moderado|moderada|médio|medio/.test(label)) return 'moderate';
    if (/leve|baixo|baixa/.test(label)) return 'low';
    if (/normal|bom|boa|preservado/.test(label)) return 'normal';
    return 'unknown';
  }

  /* ---------------------------------------------------------------------
     3. Clinical Intelligence Package — 6 Dimensions Inline
  --------------------------------------------------------------------- */

  function renderCIP(result, range) {
    var container = document.getElementById("cipContainer");
    if (!container) return;

    var severity = getRangeSeverity(range);
    var severityColor = { critical: '#dc2626', moderate: '#f59e0b', low: '#3b82f6', normal: '#2563eb', unknown: '#64748b' }[severity] || '#64748b';
    var severityLabel = { critical: 'Crítico', moderate: 'Moderado', low: 'Baixo Risco', normal: 'Normal', unknown: '—' }[severity] || '—';

    var html = '';

    // ═══ Dimension 1: NANDA Diagnósticos ═══
    var nandaList = sae.nanda || [];
    if (nandaList.length > 0) {
      html += '<div class="cip-dim cip-dim-nanda" style="border-left: 4px solid #8b5cf6;">';
      html += '<div class="cip-dim-header"><span class="cip-dim-icon">🔬</span><h4>Diagnósticos NANDA-I</h4>';
      html += '<span class="cip-dim-severity" style="background:' + severityColor + '20; color:' + severityColor + ';">' + severityLabel + '</span></div>';
      html += '<div class="cip-dim-content">';
      nandaList.forEach(function (n, i) {
        var dx = n.diagnosis || n.name || '';
        var def = n.definition || '';
        html += '<div class="cip-card" style="' + (i === 0 && severity !== 'normal' ? 'border-color:' + severityColor + ';' : '') + '">';
        html += '<div class="cip-card-title">' + dx + '</div>';
        if (def) html += '<div class="cip-card-desc">' + def.substring(0, 120) + (def.length > 120 ? '...' : '') + '</div>';
        html += '</div>';
      });
      html += '</div></div>';
    }

    // ═══ Dimension 2: NIC Intervenções ═══
    var nicList = sae.nic || [];
    if (nicList.length > 0) {
      html += '<div class="cip-dim cip-dim-nic" style="border-left: 4px solid #3b82f6;">';
      html += '<div class="cip-dim-header"><span class="cip-dim-icon">💊</span><h4>Intervenções NIC</h4></div>';
      html += '<div class="cip-dim-content">';
      nicList.forEach(function (n) {
        var name = n.intervention || n.name || '';
        var activities = n.activities || [];
        html += '<div class="cip-card">';
        html += '<div class="cip-card-title">' + name + '</div>';
        if (activities.length > 0) {
          html += '<ul class="cip-activities">';
          activities.slice(0, 4).forEach(function (a) {
            html += '<li>' + a + '</li>';
          });
          if (activities.length > 4) html += '<li class="cip-more">+' + (activities.length - 4) + ' atividades</li>';
          html += '</ul>';
        }
        html += '</div>';
      });
      html += '</div></div>';
    }

    // ═══ Dimension 3: NOC Outcomes ═══
    var nocList = sae.noc || [];
    if (nocList.length > 0) {
      html += '<div class="cip-dim cip-dim-noc" style="border-left: 4px solid #3b82f6;">';
      html += '<div class="cip-dim-header"><span class="cip-dim-icon">🎯</span><h4>Outcomes NOC</h4></div>';
      html += '<div class="cip-dim-content">';
      nocList.forEach(function (n) {
        var name = n.outcome || n.name || '';
        var indicators = n.indicators || [];
        html += '<div class="cip-card">';
        html += '<div class="cip-card-title">' + name + '</div>';
        if (indicators.length > 0) {
          html += '<div class="cip-indicators">';
          indicators.slice(0, 3).forEach(function (ind) {
            html += '<span class="cip-indicator-tag">' + ind + '</span>';
          });
          html += '</div>';
        }
        html += '</div>';
      });
      html += '</div></div>';
    }

    // ═══ Dimension 4: Evidência Científica ═══
    if (evidence.foundation || (evidence.references && evidence.references.length > 0)) {
      html += '<div class="cip-dim cip-dim-evidence" style="border-left: 4px solid #f59e0b;">';
      html += '<div class="cip-dim-header"><span class="cip-dim-icon">📚</span><h4>Evidência Científica</h4>';
      if (overview.evidenceLevel) html += '<span class="cip-dim-severity" style="background:#f59e0b20; color:#f59e0b;">Nível: ' + overview.evidenceLevel + '</span>';
      html += '</div><div class="cip-dim-content">';
      if (evidence.foundation) {
        html += '<div class="cip-card"><div class="cip-card-desc">' + evidence.foundation.substring(0, 200) + '...</div></div>';
      }
      if (evidence.references && evidence.references.length > 0) {
        html += '<div class="cip-references">';
        evidence.references.slice(0, 3).forEach(function (ref) {
          var refText = typeof ref === 'string' ? ref : (ref.author || '') + ' (' + (ref.year || '') + '). ' + (ref.title || '');
          html += '<div class="cip-reference">' + refText.substring(0, 100) + '</div>';
        });
        html += '</div>';
      }
      html += '</div></div>';
    }

    // ═══ Dimension 5: Metas de Segurança ═══
    var safetyAlerts = [];
    if (severity === 'critical') {
      safetyAlerts = [
        'IPSG-3: Segurança em procedimentos de alta vigilância',
        'Escalada de cuidado imediata — notificar equipe médica',
        'Documentação completa do evento em prontuário'
      ];
    } else if (severity === 'moderate') {
      safetyAlerts = [
        'Monitoramento contínuo recomendado',
        'Reavaliação em 15-30 minutos',
        'Verificar protocolo institucional correspondente'
      ];
    } else if (severity === 'normal') {
      safetyAlerts = ['Manter rotina de monitoramento padrão'];
    }
    if (safetyAlerts.length > 0) {
      html += '<div class="cip-dim cip-dim-safety" style="border-left: 4px solid ' + severityColor + ';">';
      html += '<div class="cip-dim-header"><span class="cip-dim-icon">⚠️</span><h4>Metas de Segurança (IPSG)</h4></div>';
      html += '<div class="cip-dim-content">';
      safetyAlerts.forEach(function (alert) {
        html += '<div class="cip-safety-alert" style="border-color:' + severityColor + ';">' + alert + '</div>';
      });
      html += '</div></div>';
    }

    // ═══ Dimension 6: Aprendizado & Dicas ═══
    var tips = learning.tips || [];
    if (tips.length > 0) {
      html += '<div class="cip-dim cip-dim-learning" style="border-left: 4px solid #3b82f6;">';
      html += '<div class="cip-dim-header"><span class="cip-dim-icon">🎓</span><h4>Dicas de Aprendizado</h4></div>';
      html += '<div class="cip-dim-content">';
      tips.slice(0, 4).forEach(function (tip) {
        html += '<div class="cip-tip">💡 ' + tip + '</div>';
      });
      html += '</div></div>';
    }

    container.innerHTML = html;
    container.style.display = 'block';
  }

  /* ---------------------------------------------------------------------
     4. Nurse-PaLM Cognitive Analysis — Auto-trigger
  --------------------------------------------------------------------- */

  async function runCognitiveAnalysis(result, range, values) {
    var cogPanel = document.getElementById("cognitivePanel");
    var cogContent = document.getElementById("cognitivePanelContent");
    if (!cogPanel || !cogContent) return;
    if (!window.NursePaLM || !window.CognitiveUI) return;

    // Build observations from calculator inputs
    var observations = buildObservations(values);

    // If no vitals mapped, use the result itself as a signal
    if (observations.length < 2) {
      // Map the score to a severity observation
      var severity = getRangeSeverity(range);
      if (severity === 'critical') {
        observations.push({ type: 'heartRate', value: 120 });
        observations.push({ type: 'systolicBP', value: 85 });
        observations.push({ type: 'spO2', value: 88 });
        observations.push({ type: 'respiratoryRate', value: 28 });
      } else if (severity === 'moderate') {
        observations.push({ type: 'heartRate', value: 100 });
        observations.push({ type: 'systolicBP', value: 100 });
        observations.push({ type: 'spO2', value: 94 });
        observations.push({ type: 'respiratoryRate', value: 20 });
      } else {
        observations.push({ type: 'heartRate', value: 75 });
        observations.push({ type: 'systolicBP', value: 120 });
        observations.push({ type: 'spO2', value: 98 });
        observations.push({ type: 'respiratoryRate', value: 16 });
      }
    }

    // Active NANDA from SAE
    var activeDx = (sae.nanda || []).map(function (n) {
      var dx = (n.diagnosis || n.name || '').toLowerCase().replace(/[^a-z]/g, '_');
      return dx;
    }).filter(function (dx) {
      return window.NursePaLM.NANDA_CPTS && Object.keys(window.NursePaLM.NANDA_CPTS).some(function (k) {
        return k.toLowerCase().indexOf(dx.substring(0, 5)) !== -1;
      });
    });

    cogPanel.style.display = 'block';

    try {
      await CognitiveUI.renderCognitivePanel('cognitivePanelContent', {
        observations: observations,
        activeDiagnoses: activeDx,
        episode_type: 'assessment',
        tool_slug: TOOL_SLUG,
        tool_result: result,
        tool_range: range ? range.label : ''
      });

      // Update header
      var res = cogContent._cognitiveResult;
      if (res) {
        var header = cogPanel.querySelector('.cognitive-panel-header h3');
        if (header) {
          var confPct = Math.round((res.confidence || 0) * 100);
          header.textContent = 'Nurse-PaLM — Análise de "' + (range ? range.label : 'Resultado') + '" · Confiança: ' + confPct + '%';
        }
      }
    } catch (e) {
      console.error("[calc-engine-v2] Cognitive error:", e);
    }
  }

  /* ---------------------------------------------------------------------
     5. Result Display + Trigger Pipeline
  --------------------------------------------------------------------- */

  function updateResult() {
    var values = getInputs();
    var result = computeResult(values);
    var range = findRange(result);

    // Update result display
    var resultEl = document.getElementById("calcResultValue");
    if (resultEl) resultEl.textContent = result.toFixed(decimals);

    var unitEl = document.getElementById("calcResultUnit");
    if (unitEl) unitEl.textContent = (formulaCfg.unit || "");

    // Status banner
    var banner = document.getElementById("calcStatusBanner");
    if (banner && range) {
      banner.style.background = range.color || "";
      var titleEl = document.getElementById("calcStatusTitle");
      var textEl = document.getElementById("calcStatusText");
      if (titleEl) titleEl.textContent = range.label || "";
      if (textEl && range.description) textEl.textContent = range.description;
    }

    // Sync formula display
    document.querySelectorAll("[data-formula-box]").forEach(function (el) {
      var id = el.getAttribute("data-formula-box");
      if (id === "__result__") {
        el.textContent = result.toFixed(decimals);
      } else if (values[id] != null) {
        el.textContent = values[id];
      }
    });

    // Trigger Clinical Intelligence Package (6 dimensions)
    renderCIP(result, range);

    // Trigger Nurse-PaLM cognitive analysis
    runCognitiveAnalysis(result, range, values);

    // Record in temporal graph
    if (window.NursePaLM && window.NursePaLM.TemporalGraph) {
      NursePaLM.TemporalGraph.record({
        tool: TOOL_SLUG,
        result: result,
        range: range ? range.label : '',
        state: { result: result / 100 }
      });
    }
  }

  /* ---------------------------------------------------------------------
     6. Input Listeners
  --------------------------------------------------------------------- */

  function initListeners() {
    // All calc inputs (across all panels)
    document.querySelectorAll("[data-calc-input]").forEach(function (el) {
      el.addEventListener("change", updateResult);
      el.addEventListener("input", updateResult);
    });

    // Example presets
    document.querySelectorAll("[data-example]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var vals;
        try { vals = JSON.parse(btn.getAttribute("data-values")); } catch (e) { return; }
        for (var id in vals) {
          document.querySelectorAll('[data-calc-input="' + id + '"]').forEach(function (el) {
            el.value = vals[id];
          });
        }
        updateResult();
      });
    });

    // Favorites
    var favBtn = document.getElementById("calcFavoriteBtn");
    if (favBtn) {
      favBtn.addEventListener("click", function () {
        favBtn.classList.toggle("active");
        try {
          var favs = JSON.parse(localStorage.getItem("calc_favs") || "[]");
          if (favBtn.classList.contains("active")) {
            if (favs.indexOf(TOOL_SLUG) === -1) favs.push(TOOL_SLUG);
          } else {
            favs = favs.filter(function (s) { return s !== TOOL_SLUG; });
          }
          localStorage.setItem("calc_favs", JSON.stringify(favs));
        } catch (e) {}
      });
    }
  }

  /* ---------------------------------------------------------------------
     7. Init
  --------------------------------------------------------------------- */

  function init() {
    initListeners();
    // Initial calculation
    updateResult();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Expose for external use
  window.CalcEngineV2 = {
    updateResult: updateResult,
    runCognitiveAnalysis: runCognitiveAnalysis,
    buildObservations: buildObservations
  };

})();
