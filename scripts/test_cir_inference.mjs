#!/usr/bin/env node
/** Testes CIR — Apgar e Glasgow GCS (Fases 3–4). */
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

function loadGraph(name) {
  const edgesPath = join(root, "NIFS/DELIVERY/js/modules/data", name);
  return JSON.parse(readFileSync(edgesPath, "utf8"));
}

function evalScoreCondition(condition, score) {
  const expr = String(condition).trim();
  if (!/^[\d\s<>=.!&|score]+$/.test(expr)) return false;
  return !!Function("score", `return (${expr});`)(Number(score));
}

function matchInferenceRule(inferenceRules, score) {
  for (const block of inferenceRules || []) {
    for (const rule of block.rules || []) {
      if (evalScoreCondition(rule.condition, score)) {
        return { rule_id: block.rule_id, label: rule.label, nanda_boost: rule.nanda_boost || {} };
      }
    }
  }
  return null;
}

function edgesFrom(graph, fromId, relationTypes) {
  return (graph.edges || [])
    .filter((e) => e.from === fromId && relationTypes.includes(e.relation_type))
    .sort((a, b) => (b.weight || 0) - (a.weight || 0));
}

function infer(graph, score) {
  const matched = matchInferenceRule(graph.inference_rules, score);
  const diagnoses = Object.entries(matched?.nanda_boost || {})
    .map(([code, probability]) => ({ code, probability }))
    .sort((a, b) => b.probability - a.probability);
  const top = diagnoses[0];
  const nics = top ? edgesFrom(graph, top.code, ["treated_by", "maps_to"]) : [];
  const nocs = [];
  nics.slice(0, 2).forEach((nic) => {
    edgesFrom(graph, nic.to, ["impacts"]).forEach((e) => nocs.push(e.to));
  });
  return { matched: matched?.label, topNanda: top?.code, nics: nics.map((e) => e.to), nocs };
}

const suites = [
  {
    name: "apgar",
    graph: loadGraph("apgar-edges.json"),
    cases: [
      { score: 3, expectLabel: "severe_distress", expectNanda: "NANDA_00162" },
      { score: 5, expectLabel: "moderate_distress", expectNanda: "NANDA_00162" },
      { score: 10, expectLabel: "stable", expectNanda: "NANDA_00162" },
    ],
  },
  {
    name: "glasgow",
    graph: loadGraph("glasgow-edges.json"),
    cases: [
      { score: 6, expectLabel: "severe", expectNanda: "NANDA_00226" },
      { score: 10, expectLabel: "moderate", expectNanda: "NANDA_00226" },
      { score: 14, expectLabel: "mild", expectNanda: "NANDA_00226" },
    ],
  },
];

let failed = 0;
for (const suite of suites) {
  for (const c of suite.cases) {
    const r = infer(suite.graph, c.score);
    const ok =
      r.matched === c.expectLabel &&
      r.topNanda === c.expectNanda &&
      r.nics.length > 0 &&
      r.nocs.length > 0;
    if (!ok) {
      console.error(`FAIL [${suite.name}] score`, c.score, r);
      failed++;
    } else {
      console.log(`OK [${suite.name}] score`, c.score, "→", r.matched, r.nics[0], r.nocs[0]);
    }
  }
}

if (failed) process.exit(1);
console.log("All CIR inference tests passed.");
