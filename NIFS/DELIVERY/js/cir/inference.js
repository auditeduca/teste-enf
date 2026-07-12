/* ======================================================================
   cir/inference.js — CIR mínimo: score + apgar-edges → NANDA/NIC/NOC (Fase 3)
   Fonte: ToolCKO.edges (gerado de reference-datasets/ontology/apgar_edges.json)
   ====================================================================== */
(function (global) {
  "use strict";

  var NANDA_REL = ["supports_diagnosis", "triggers", "treated_by", "maps_to"];
  var NIC_FROM_NANDA = ["treated_by", "maps_to"];
  var NIC_TO_NOC = ["impacts"];

  function parseNandaCode(edgeId) {
    if (!edgeId) return "";
    var m = String(edgeId).match(/NANDA[_\.]?0*(\d+)/i);
    return m ? m[1].padStart(5, "0") : edgeId;
  }

  function parseNicCode(edgeId) {
    if (!edgeId) return "";
    var m = String(edgeId).match(/NIC[_\.]?0*(\d+)/i);
    return m ? m[1] : edgeId;
  }

  function parseNocCode(edgeId) {
    if (!edgeId) return "";
    var m = String(edgeId).match(/NOC[_\.]?0*(\d+)/i);
    return m ? m[1].padStart(4, "0") : edgeId;
  }

  function evalScoreCondition(condition, score) {
    if (!condition) return false;
    var expr = String(condition).trim();
    if (!/^[\d\s<>=.!&|score]+$/.test(expr)) return false;
    try {
      return !!Function("score", "return (" + expr + ");")(Number(score));
    } catch (e) {
      return false;
    }
  }

  function matchInferenceRule(inferenceRules, score) {
    var blocks = inferenceRules || [];
    for (var i = 0; i < blocks.length; i++) {
      var rules = blocks[i].rules || [];
      for (var j = 0; j < rules.length; j++) {
        if (evalScoreCondition(rules[j].condition, score)) {
          return {
            rule_id: blocks[i].rule_id,
            label: rules[j].label,
            nanda_boost: rules[j].nanda_boost || {},
          };
        }
      }
    }
    return null;
  }

  function edgesFrom(graph, fromId, relationTypes) {
    var out = [];
    (graph.edges || []).forEach(function (e) {
      if (e.from === fromId && relationTypes.indexOf(e.relation_type) >= 0) {
        out.push(e);
      }
    });
    out.sort(function (a, b) {
      return (b.weight || 0) - (a.weight || 0);
    });
    return out;
  }

  function labelFor(kind, edgeOrCanonical, labelFn) {
    if (!labelFn) return edgeOrCanonical;
    var code =
      kind === "nanda"
        ? parseNandaCode(edgeOrCanonical)
        : kind === "nic"
          ? parseNicCode(edgeOrCanonical)
          : parseNocCode(edgeOrCanonical);
    var lbl = labelFn(kind, code);
    return lbl || edgeOrCanonical;
  }

  /**
   * @param {object} graph — apgar-edges.json
   * @param {number} score — total calculado
   * @param {{ label?: function }} options — resolve terminologia (ClinicalTerminology.label)
   */
  function infer(graph, score, options) {
    options = options || {};
    var labelFn = options.label;
    var matched = matchInferenceRule(graph.inference_rules, score);

    var diagnoses = [];
    if (matched && matched.nanda_boost) {
      Object.keys(matched.nanda_boost).forEach(function (nandaKey) {
        diagnoses.push({
          code: nandaKey,
          nanda_code: parseNandaCode(nandaKey),
          name: labelFor("nanda", nandaKey, labelFn),
          probability: matched.nanda_boost[nandaKey],
          evidence: [matched.label, matched.rule_id].filter(Boolean),
        });
      });
      diagnoses.sort(function (a, b) {
        return (b.probability || 0) - (a.probability || 0);
      });
    }

    var interventions = [];
    var outcomes = [];
    var topNanda = diagnoses[0];

    if (topNanda) {
      edgesFrom(graph, topNanda.code, NIC_FROM_NANDA).forEach(function (e) {
        interventions.push({
          code: e.to,
          nic_code: parseNicCode(e.to),
          intervention: labelFor("nic", e.to, labelFn),
          name: labelFor("nic", e.to, labelFn),
          weight: e.weight,
          notes: e.notes || "",
          activities: e.notes ? [e.notes] : [],
        });
      });

      interventions.slice(0, 3).forEach(function (nic) {
        edgesFrom(graph, nic.code, NIC_TO_NOC).forEach(function (e) {
          var nocCode = parseNocCode(e.to);
          var exists = outcomes.some(function (o) {
            return o.noc_code === nocCode;
          });
          if (!exists) {
            outcomes.push({
              code: e.to,
              noc_code: nocCode,
              outcome: labelFor("noc", e.to, labelFn),
              name: labelFor("noc", e.to, labelFn),
              weight: e.weight,
              indicators: [],
            });
          }
        });
      });
      outcomes.sort(function (a, b) {
        return (b.weight || 0) - (a.weight || 0);
      });
    }

    var plan = interventions[0]
      ? {
          nic_code: interventions[0].code,
          name: interventions[0].name,
        }
      : null;

    return {
      source: "cir-edges",
      score: score,
      matched_rule: matched,
      diagnoses: diagnoses,
      interventions: interventions,
      outcomes: outcomes,
      plan: plan,
      confidence: diagnoses[0] ? diagnoses[0].probability : 0.5,
    };
  }

  global.CIRInference = {
    infer: infer,
    parseNandaCode: parseNandaCode,
    parseNicCode: parseNicCode,
    parseNocCode: parseNocCode,
    evalScoreCondition: evalScoreCondition,
    matchInferenceRule: matchInferenceRule,
  };
})(typeof window !== "undefined" ? window : globalThis);
