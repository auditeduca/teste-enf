#!/usr/bin/env node
import { readFileSync, writeFileSync, mkdirSync, readdirSync, existsSync, copyFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { CASCADE, RULES, runGates, RUNTIME_PAGES } from "./public/engine/core.js";

const root = dirname(fileURLToPath(import.meta.url));
const gatePub = join(root, "public");
const site = join(root, "../reference-website");
const policy = JSON.parse(readFileSync(join(gatePub, "policies/fail-closed.json"), "utf8"));
if (!policy.root || policy.kind !== "policy-as-code" || JSON.stringify(policy.cascade) !== JSON.stringify(CASCADE)) {
  console.error("CKO GATE FAIL policy-as-code root mismatch");
  process.exit(1);
}
const universe = JSON.parse(readFileSync(join(gatePub, "data/universe.json"), "utf8"));
const listing = readdirSync(site);
const files = Object.fromEntries(
  [...RUNTIME_PAGES, "aldrete.html"].filter((p) => existsSync(join(site, p))).map((p) => [p, readFileSync(join(site, p), "utf8")])
);
const toolLibraryPath = existsSync(join(site, "data/cko/tool-library-runtime.json"))
  ? join(site, "data/cko/tool-library-runtime.json")
  : join(gatePub, "data/tool-library-runtime.json");
const toolLibrary = existsSync(toolLibraryPath) ? JSON.parse(readFileSync(toolLibraryPath, "utf8")) : undefined;
const governancePath = join(site, "data/cko/governance.json");
const governance = existsSync(governancePath) ? JSON.parse(readFileSync(governancePath, "utf8")) : undefined;
const layersPath = join(site, "data/cko/layers.json");
const layers = existsSync(layersPath) ? JSON.parse(readFileSync(layersPath, "utf8")) : undefined;
const pendenciesPath = join(gatePub, "data/pendencies.json");
const pendencies = existsSync(pendenciesPath) ? JSON.parse(readFileSync(pendenciesPath, "utf8")) : undefined;
const driveImmutablePath = join(gatePub, "data/drive-immutable.json");
const driveImmutable = existsSync(driveImmutablePath) ? JSON.parse(readFileSync(driveImmutablePath, "utf8")) : undefined;
const ontology = existsSync(join(gatePub, "graph/ontology.ttl")) ? readFileSync(join(gatePub, "graph/ontology.ttl"), "utf8") : "";
const platform = { listing, files, toolLibrary, governance, layers, pendencies, driveImmutable };

const report = await runGates(universe, { action: "inspect", platform, ontology });

const outDir = join(gatePub, "data");
mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, "gate-report.json"), JSON.stringify(report, null, 2) + "\n");
writeFileSync(
  join(outDir, "evidence-index.json"),
  JSON.stringify(
    {
      receipts_n: report.receipts_n,
      evidence_ok: report.evidence.ok,
      coverage_ok: report.coverage.ok,
      residual_uncertainty: report.residual_uncertainty.value,
      release: report.release,
    },
    null,
    2
  ) + "\n"
);

const cascadeDir = join(site, "data/cko/cascade");
mkdirSync(cascadeDir, { recursive: true });
const cascadeIndex = {
  id: "CKO-ASSURANCE-CASCADE-1.0.0",
  kind: "assurance-cascade",
  root: "policy-as-code",
  starts_at: report.starts_at,
  cascade: CASCADE,
  rules: RULES,
  release_allowed: false,
  release: report.release,
  coverage: report.coverage.ratio,
  evidence: report.evidence.ratio,
  residual_uncertainty: report.residual_uncertainty.value,
  unknown_universe: (report.unknown_universe || []).map((u) => u.id),
  verification: {
    shacl: report.verification?.shacl?.ok === true,
    temporal: report.verification?.temporal?.ok === true,
    rdf: report.verification?.rdf?.ok === true,
    reasoning: report.verification?.reasoning?.ok === true,
    contracts: report.verification?.contracts?.ok === true,
    fuzz_n: report.verification?.fuzz?.n,
    fuzz_false_accept: report.verification?.fuzz?.false_accept,
    mutation: report.verification?.mutations?.ok === true,
    model_states: report.verification?.model?.states,
    security: report.verification?.security?.ok === true,
  },
  evaluation: {
    precision: report.evaluation.precision,
    recall: report.evaluation.recall,
    kappa: report.evaluation.inter_rater.kappa,
    psi: report.evaluation.drift.psi,
    brier: report.evaluation.calibration.brier,
    synthetic: true,
    production_nursepalm: false,
  },
  orchestrator: {
    pattern: report.orchestrator.pattern,
    semantics: report.orchestrator.semantics,
    retries: report.orchestrator.retries,
  },
};
writeFileSync(join(cascadeDir, "index.json"), JSON.stringify(cascadeIndex, null, 2) + "\n");
writeFileSync(
  join(cascadeDir, "gate-report.json"),
  JSON.stringify(
    {
      starts_at: report.starts_at,
      cascade: report.cascade,
      rules: report.rules,
      release_allowed: false,
      coverage: report.coverage,
      evidence: { ok: report.evidence.ok, ratio: report.evidence.ratio, known: report.evidence.known, evidenced: report.evidence.evidenced },
      residual_uncertainty: report.residual_uncertainty,
      unknown_universe: report.unknown_universe,
      verification: report.verification,
      evaluation: {
        golden_n: report.evaluation.golden_n,
        precision: report.evaluation.precision,
        recall: report.evaluation.recall,
        f1: report.evaluation.f1,
        confusion: report.evaluation.confusion,
        inter_rater: report.evaluation.inter_rater,
        calibration: report.evaluation.calibration,
        adversarial: report.evaluation.adversarial,
        drift: report.evaluation.drift,
        synthetic: report.evaluation.synthetic,
        production_nursepalm: report.evaluation.production_nursepalm,
        ok: report.evaluation.ok,
      },
      orchestrator: {
        pattern: report.orchestrator.pattern,
        semantics: report.orchestrator.semantics,
        retries: report.orchestrator.retries,
        acked: report.orchestrator.acked,
        dlq: report.orchestrator.dlq,
        saga: report.orchestrator.saga,
      },
    },
    null,
    2
  ) + "\n"
);
copyFileSync(join(gatePub, "graph/ontology.ttl"), join(cascadeDir, "ontology.ttl"));
copyFileSync(join(gatePub, "graph/shacl.json"), join(cascadeDir, "shacl.json"));
writeFileSync(
  join(cascadeDir, "index.html"),
  `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>CKO cascade HOLD</title></head><body><main><h1>Assurance cascade</h1><p>HOLD / NOT_RELEASED. <code>release_allowed: false</code>.</p><p><a href="./index.json">index.json</a> · <a href="./gate-report.json">gate-report.json</a></p></main></body></html>\n`
);

const failed = report.failed.map((g) => g.id);
if (!report.ok) {
  console.error("CKO GATE FAIL", failed);
  process.exit(1);
}
console.log("CKO GATE PASS");
console.log(JSON.stringify({
  starts_at: report.starts_at,
  cascade: report.cascade.map((g) => `${g.id}:${g.status}`),
  coverage: report.coverage.ratio,
  evidence: report.evidence.ratio,
  tests_defined_pass: 1,
  residual_uncertainty: report.residual_uncertainty.value,
  unknown: report.unknown_universe.length,
  release: report.release,
  site: "reference-website",
}, null, 2));
