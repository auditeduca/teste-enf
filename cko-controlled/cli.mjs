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
const mdRegPolicyPath = join(gatePub, "policies/md-reg-frontend.json");
const mdRegPolicy = existsSync(mdRegPolicyPath) ? JSON.parse(readFileSync(mdRegPolicyPath, "utf8")) : undefined;
const humanPath = existsSync(join(site, "data/cko/human-decisions.json"))
  ? join(site, "data/cko/human-decisions.json")
  : join(gatePub, "data/human-decisions.json");
const humanDecisions = existsSync(humanPath) ? JSON.parse(readFileSync(humanPath, "utf8")) : undefined;
const dsPath = existsSync(join(site, "data/cko/design-system.json"))
  ? join(site, "data/cko/design-system.json")
  : join(gatePub, "data/design-system.json");
const designSystem = existsSync(dsPath) ? JSON.parse(readFileSync(dsPath, "utf8")) : undefined;
const utPath = existsSync(join(site, "data/cko/universal-tool.json"))
  ? join(site, "data/cko/universal-tool.json")
  : join(gatePub, "policies/universal-tool.json");
const universalToolPolicy = existsSync(utPath) ? JSON.parse(readFileSync(utPath, "utf8")) : undefined;
const masterPath = existsSync(join(site, "data/cko/policy-master.json"))
  ? join(site, "data/cko/policy-master.json")
  : join(gatePub, "policies/policy-master.json");
const policyMaster = existsSync(masterPath) ? JSON.parse(readFileSync(masterPath, "utf8")) : undefined;
const vasPath = existsSync(join(site, "data/cko/visual-assets.json"))
  ? join(site, "data/cko/visual-assets.json")
  : join(gatePub, "policies/visual-assets.json");
const visualAssetPolicy = existsSync(vasPath) ? JSON.parse(readFileSync(vasPath, "utf8")) : undefined;
const platformClosure = JSON.parse(readFileSync(join(gatePub, "policies/platform-closure.json"), "utf8"));
const layerPolicies = JSON.parse(readFileSync(join(gatePub, "policies/layer-policies.json"), "utf8"));
const extractionPolicy = JSON.parse(readFileSync(join(gatePub, "policies/extraction.json"), "utf8"));
const apiCatalog = JSON.parse(readFileSync(join(gatePub, "policies/api-catalog.json"), "utf8"));
const governedFabric = JSON.parse(readFileSync(join(gatePub, "policies/governed-fabric.json"), "utf8"));
const ontology = existsSync(join(gatePub, "graph/ontology.ttl")) ? readFileSync(join(gatePub, "graph/ontology.ttl"), "utf8") : "";
const platform = {
  listing,
  files,
  toolLibrary,
  governance,
  layers,
  pendencies,
  driveImmutable,
  mdRegPolicy,
  humanDecisions,
  designSystem,
  universalToolPolicy,
  policyMaster,
  visualAssetPolicy,
  platformClosure,
  layerPolicies,
  extractionPolicy,
  apiCatalog,
  governedFabric,
};

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
copyFileSync(join(gatePub, "policies/md-reg-frontend.json"), join(cascadeDir, "md-reg-frontend.json"));
copyFileSync(join(gatePub, "policies/md-reg-frontend.json"), join(site, "data/cko/md-reg-frontend.json"));
if (universalToolPolicy) {
  writeFileSync(join(cascadeDir, "universal-tool.json"), JSON.stringify(universalToolPolicy, null, 2) + "\n");
  writeFileSync(join(site, "data/cko/universal-tool.json"), JSON.stringify(universalToolPolicy, null, 2) + "\n");
}
if (policyMaster) {
  writeFileSync(join(cascadeDir, "policy-master.json"), JSON.stringify(policyMaster, null, 2) + "\n");
  writeFileSync(join(site, "data/cko/policy-master.json"), JSON.stringify(policyMaster, null, 2) + "\n");
}
if (visualAssetPolicy) {
  writeFileSync(join(cascadeDir, "visual-assets.json"), JSON.stringify(visualAssetPolicy, null, 2) + "\n");
  writeFileSync(join(site, "data/cko/visual-assets.json"), JSON.stringify(visualAssetPolicy, null, 2) + "\n");
}
if (humanDecisions) {
  writeFileSync(join(cascadeDir, "human-decisions.json"), JSON.stringify(humanDecisions, null, 2) + "\n");
  writeFileSync(join(site, "data/cko/human-decisions.json"), JSON.stringify(humanDecisions, null, 2) + "\n");
}
const holdPacks = [
  ["platform-closure.json", platformClosure],
  ["layer-policies.json", layerPolicies],
  ["extraction.json", extractionPolicy],
  ["api-catalog.json", apiCatalog],
  ["governed-fabric.json", governedFabric],
];
for (const [name, payload] of holdPacks) {
  writeFileSync(join(cascadeDir, name), JSON.stringify(payload, null, 2) + "\n");
  writeFileSync(join(site, "data/cko", name), JSON.stringify(payload, null, 2) + "\n");
}
writeFileSync(
  join(cascadeDir, "index.html"),
  `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cascata de garantia | Calculadoras de Enfermagem</title>
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#1A3E74">
<link rel="stylesheet" href="/css/cko-ds.css">
</head>
<body class="cko-ds-body" data-cko-status="CANDIDATE_HOLD_RELEASE" data-cko-cascade="policy-as-code" data-cko-release="HOLD_NOT_RELEASED">
<a class="cko-ds-skip" href="#main-content">Pular para o conteúdo principal</a>
<main id="main-content" class="cko-ds-page">
<nav class="cko-ds-crumbs" aria-label="Breadcrumb"><a href="/">Início</a> › <a href="/cko-estado.html">Como está a plataforma</a> › <a href="/ecossistema.html">Ecossistema</a> › <span>Cascata</span></nav>
<div id="cko-ds-root" data-cko-ds-render="cascade" data-cko-ds-src="/data/cko/design-system.json"></div>
<div data-cko-ds-render="universal-tool" data-cko-ds-src="/data/cko/universal-tool.json"></div>
<div data-cko-ds-render="policy-master" data-cko-ds-src="/data/cko/policy-master.json"></div>
<div data-cko-ds-render="visual-assets" data-cko-ds-src="/data/cko/visual-assets.json"></div>
<div data-cko-ds-render="platform-closure" data-cko-ds-src="/data/cko/platform-closure.json"></div>
<div data-cko-ds-render="layer-policies" data-cko-ds-src="/data/cko/layer-policies.json"></div>
<div data-cko-ds-render="extraction" data-cko-ds-src="/data/cko/extraction.json"></div>
<div data-cko-ds-render="api-catalog" data-cko-ds-src="/data/cko/api-catalog.json"></div>
<div data-cko-ds-render="governed-fabric" data-cko-ds-src="/data/cko/governed-fabric.json"></div>
<p class="cko-ds-help"><a class="cko-ds-link" href="./index.json">index.json</a> · <a class="cko-ds-link" href="./gate-report.json">gate-report.json</a></p>
</main>
<script type="module" src="/js/cko-ds-render.js?v=pmc-5"></script>
</body>
</html>
`
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
