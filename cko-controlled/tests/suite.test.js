import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  validateSchema,
  validateRuntimePlatformSchema,
  validateToolLibrarySchema,
  inspectPendencies,
  inspectCalenfGovernance,
  inspectLayers,
  inspectMdRegPolicy,
  inspectHumanDecisions,
  inspectDesignSystem,
  inspectUniversalToolPolicy,
  inspectPolicyMaster,
  inspectTemplateGovernance,
  inspectVisualAssetPolicy,
  inspectPlatformClosure,
  inspectLayerPolicies,
  inspectExtractionPolicy,
  inspectApiCatalog,
  inspectGovernedFabric,
  LAYER_CATALOG_ID,
  LAYER_DOCUMENT_ID,
  LAYER_POLICY_N,
  EXTRACTION_POLICY_ID,
  EXTRACTION_DOCUMENT_ID,
  EXTRACTION_STREAM_N,
  API_CATALOG_ID,
  API_DOCUMENT_ID,
  API_FAMILY_N,
  API_ENDPOINT_TOTAL,
  FABRIC_POLICY_ID,
  FABRIC_DOCUMENT_ID,
  FABRIC_FAMILY_N,
  FABRIC_ITEM_TOTAL,
  ASSURE_TECH_IDS,
  AGENT_TOOL_IDS,
  POLICY_MASTER_FIELDS,
  CLOSURE_POLICY_ID,
  CLOSURE_DOCUMENT_ID,
  HOLD_POLICY_N,
  MD_REG_CHAIN,
  MD_REG_POLICY_ID,
  UT_POLICY_ID,
  UT_DOCUMENT_ID,
  UT_CONTROL_N,
  UT_MD_GATE,
  POLICY_MASTER_ID,
  POLICY_MASTER_FIELD_N,
  VAS_POLICY_ID,
  VAS_FAMILY_N,
  VAS_INTERNAL_POLICY_N,
  HOLD_HUMAN_STATUS,
  validatePendenciesSchema,
  evaluatePolicies,
  graphConstraints,
  coverageReport,
  evidenceCoverage,
  runtimeAssertions,
  evaluationScience,
  propertyBased,
  orchestrator,
  automaticEvidence,
  runGates,
  knownUniverseObjects,
  validateShacl,
  temporalGraph,
  projectRdf,
  reasonGraph,
  contractTest,
  fuzzRelease,
  mutationTesting,
  modelCheckReleaseInvariant,
  securityOffensive,
  CASCADE,
  RUNTIME_PAGES,
  TOOL_RUNTIME_CANARIES,
  LIBRARY_RUNTIME_CANARIES,
  TOOL_ENGINE_LIBS,
  CANONICAL_LAYER_IDS,
} from "../public/engine/core.js";

const root = dirname(fileURLToPath(import.meta.url));
const gatePub = join(root, "../public");
const site = join(root, "../../reference-website");
const universe = JSON.parse(readFileSync(join(gatePub, "data/universe.json"), "utf8"));
const toolLibrary = JSON.parse(readFileSync(join(site, "data/cko/tool-library-runtime.json"), "utf8"));
const governance = JSON.parse(readFileSync(join(site, "data/cko/governance.json"), "utf8"));
const layers = JSON.parse(readFileSync(join(site, "data/cko/layers.json"), "utf8"));
const pendencies = JSON.parse(readFileSync(join(gatePub, "data/pendencies.json"), "utf8"));
const driveImmutable = JSON.parse(readFileSync(join(gatePub, "data/drive-immutable.json"), "utf8"));
const mdRegPolicy = JSON.parse(readFileSync(join(gatePub, "policies/md-reg-frontend.json"), "utf8"));
const humanDecisions = JSON.parse(readFileSync(join(gatePub, "data/human-decisions.json"), "utf8"));
const designSystem = JSON.parse(readFileSync(join(site, "data/cko/design-system.json"), "utf8"));
const universalToolPolicy = JSON.parse(readFileSync(join(gatePub, "policies/universal-tool.json"), "utf8"));
const policyMaster = JSON.parse(readFileSync(join(gatePub, "policies/policy-master.json"), "utf8"));
const visualAssetPolicy = JSON.parse(readFileSync(join(gatePub, "policies/visual-assets.json"), "utf8"));
const platformClosure = JSON.parse(readFileSync(join(gatePub, "policies/platform-closure.json"), "utf8"));
const layerPolicies = JSON.parse(readFileSync(join(gatePub, "policies/layer-policies.json"), "utf8"));
const extractionPolicy = JSON.parse(readFileSync(join(gatePub, "policies/extraction.json"), "utf8"));
const apiCatalog = JSON.parse(readFileSync(join(gatePub, "policies/api-catalog.json"), "utf8"));
const governedFabric = JSON.parse(readFileSync(join(gatePub, "policies/governed-fabric.json"), "utf8"));
const platform = {
  listing: readdirSync(site),
  files: Object.fromEntries(
    [...RUNTIME_PAGES, "aldrete.html", "imc.html", "gotejamento.html", "biblioteca.html"].map((p) => [
      p,
      readFileSync(join(site, p), "utf8"),
    ])
  ),
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

describe("schemas", () => {
  it("accepts the controlled universe", () => {
    const r = validateSchema(universe);
    assert.equal(r.ok, true, r.errors.join("; "));
  });
  it("rejects a released baseline as schema-invalid", () => {
    const clone = structuredClone(universe);
    clone.baseline.release = "RELEASED";
    const r = validateSchema(clone);
    assert.equal(r.ok, false);
  });
  it("accepts the Drive Wave2 runtime platform schema", () => {
    const r = validateSchema(universe, platform);
    assert.equal(r.ok, true, r.errors.join("; "));
    const plat = validateRuntimePlatformSchema(platform);
    assert.equal(plat.ok, true, plat.errors.join("; "));
  });
  it("rejects a missing runtime page as schema-invalid", () => {
    const broken = { listing: platform.listing, files: { ...platform.files } };
    delete broken.files["missao.html"];
    const r = validateRuntimePlatformSchema(broken);
    assert.equal(r.ok, false);
    assert.ok(r.errors.some((e) => e.includes("missao.html")));
  });
});

describe("policy-as-code", () => {
  it("declares the cascade in fail-closed.json as the executable root", () => {
    const policy = JSON.parse(readFileSync(join(gatePub, "policies/fail-closed.json"), "utf8"));
    const schema = JSON.parse(readFileSync(join(gatePub, "schemas/runtime-platform.schema.json"), "utf8"));
    assert.equal(policy.root, true);
    assert.equal(policy.kind, "policy-as-code");
    assert.deepEqual(policy.cascade, CASCADE);
    assert.deepEqual(schema.properties.pages.items.enum, RUNTIME_PAGES);
    assert.ok(policy.rules.some((r) => r.id === "NO_REPORT_DASHBOARD"));
    assert.ok(policy.rules.some((r) => r.id === "RUNTIME_IS_DRIVE_PLATFORM"));
    assert.ok(policy.rules.some((r) => r.id === "TOOL_RUNTIME_PRESENT"));
    assert.ok(policy.rules.some((r) => r.id === "LIBRARY_RUNTIME_PRESENT"));
    assert.ok(policy.rules.some((r) => r.id === "TOOL_LIBRARIES_PRESENT"));
    assert.ok(policy.rules.some((r) => r.id === "SCHEMA_GOVERNS_RUNTIME"));
    assert.ok(policy.rules.some((r) => r.id === "GRAPH_GOVERNS_RUNTIME"));
    assert.ok(policy.rules.some((r) => r.id === "TWIN_GOVERNS_RUNTIME"));
    assert.ok(policy.rules.some((r) => r.id === "NURSEPALM_GOVERNS_RUNTIME"));
    assert.ok(policy.rules.some((r) => r.id === "AGENTIC_GOVERNS_RUNTIME"));
    assert.ok(policy.rules.some((r) => r.id === "PENDENCIES_EXPLICIT"));
    assert.ok(policy.rules.some((r) => r.id === "DRIVE_IMMUTABLE"));
    assert.ok(policy.rules.some((r) => r.id === "LAYERS_44_PRESENT"));
    assert.ok(policy.rules.some((r) => r.id === "MD_NORMS_EVIDENCE_CHAIN"));
    assert.ok(policy.rules.some((r) => r.id === "CASCADE_DECLARED"));
    assert.ok(policy.rules.some((r) => r.id === "HOLD_HUMAN_NON_BLOCKING"));
    assert.ok(policy.rules.some((r) => r.id === "MD_REG_IS_POLICY"));
    assert.ok(policy.rules.some((r) => r.id === "DS_STARTS_AT_POLICY"));
    assert.ok(policy.rules.some((r) => r.id === "UT_POLICY_HOLD"));
    assert.ok(policy.rules.some((r) => r.id === "POLICY_MASTER_HOLD"));
    assert.ok(policy.rules.some((r) => r.id === "TEMPLATE_POLICY_HOLD"));
    assert.ok(policy.rules.some((r) => r.id === "PLATFORM_CLOSURE_HOLD"));
    assert.ok(policy.rules.some((r) => r.id === "LAYER_POLICY_HOLD"));
    assert.ok(policy.rules.some((r) => r.id === "EXTRACTION_POLICY_HOLD"));
    assert.ok(policy.rules.some((r) => r.id === "API_CATALOG_HOLD"));
    assert.ok(policy.rules.some((r) => r.id === "GOVERNED_FABRIC_HOLD"));
  });
  it("is fail-closed on inspect", () => {
    const r = evaluatePolicies(universe, { action: "inspect" });
    assert.equal(r.release_allowed, false);
    assert.equal(r.mode, "fail-closed");
  });
  it("denies release", () => {
    const r = evaluatePolicies(universe, { action: "release" });
    assert.equal(r.ok, false);
    assert.ok(r.denials.some((d) => d.id === "B9_HOLD_BLOCKS_RELEASE"));
    assert.ok(r.denials.some((d) => d.id === "RECERT_FAIL_BLOCKS_RELEASE"));
  });
  it("denies fact without evidence", () => {
    const r = evaluatePolicies(universe, { fact: true, evidence: null });
    assert.ok(r.denials.some((d) => d.id === "NO_FACT_WITHOUT_EVIDENCE"));
  });
  it("denies PENDING as ACK", () => {
    const r = evaluatePolicies(universe, { claimed_ack: true, event_state: "PENDING" });
    assert.ok(r.denials.some((d) => d.id === "PENDING_IS_NOT_ACK"));
  });
  it("denies inferred observed runtime", () => {
    const r = evaluatePolicies(universe, { runtime_claim: "observed", runtime_source: "inferred" });
    assert.ok(r.denials.some((d) => d.id === "RUNTIME_OBSERVED_NOT_INFERRED"));
  });
  it("denies clinical claim from classification", () => {
    const r = evaluatePolicies(universe, { claim: "clinical_operational", source: "technical_classification" });
    assert.ok(r.denials.some((d) => d.id === "NO_CLINICAL_CLAIM_FROM_CLASSIFICATION"));
  });
});

describe("graph constraints", () => {
  it("closes fan-in into B9 and identities", () => {
    const r = graphConstraints(universe);
    assert.equal(r.ok, true, r.violations.join("; "));
    assert.equal(r.nodes, 13);
    assert.ok(r.edges >= 14);
  });
  it("requires the 12 Wave2 pages without a control-room graph canvas", () => {
    const r = graphConstraints(universe, platform);
    assert.equal(r.ok, true, r.violations.join("; "));
    assert.equal(r.pages, 12);
    const poisoned = {
      files: { ...platform.files, "objetivo.html": '<html><canvas id="graph"></canvas></html>' },
    };
    const bad = graphConstraints(universe, poisoned);
    assert.equal(bad.ok, false);
    assert.ok(bad.violations.some((v) => v.includes("objetivo.html")));
  });
});

describe("coverage rules", () => {
  it("covers 100% of the known universe", () => {
    const r = coverageReport(universe);
    assert.equal(r.ok, true, r.missing.join(","));
    assert.equal(r.ratio, 1);
  });
  it("evidences 100% of known objects", async () => {
    const receipts = await automaticEvidence(universe, { now: "2026-09-03T00:00:00.000Z" });
    const r = evidenceCoverage(universe, receipts);
    assert.equal(r.ok, true, r.missing.slice(0, 8).join(","));
    assert.equal(r.ratio, 1);
    assert.equal(receipts.length, knownUniverseObjects(universe).length);
  });
  it("evidences the 12 runtime pages when the platform is in the cascade", async () => {
    const receipts = await automaticEvidence(universe, { platform, now: "2026-09-03T00:00:00.000Z" });
    const r = evidenceCoverage(universe, receipts, platform);
    assert.equal(r.ok, true, r.missing.slice(0, 8).join(","));
    assert.equal(r.ratio, 1);
    assert.equal(receipts.filter((x) => x.kind === "runtime").length, 12);
    assert.ok(receipts.some((x) => x.subject === "CKO-TOOL-LIBRARY-RUNTIME-1.0.0"));
    assert.ok(receipts.some((x) => x.subject === UT_POLICY_ID));
    assert.ok(receipts.some((x) => x.subject === POLICY_MASTER_ID));
    assert.ok(receipts.some((x) => x.subject === VAS_POLICY_ID));
    assert.ok(receipts.every((x) => x.root === "policy-as-code" && x.no_fact_without_evidence === true));
  });
  it("quantifies residual uncertainty X", () => {
    assert.equal(universe.residual_uncertainty.id, "X");
    assert.ok(universe.residual_uncertainty.value > 0);
    assert.ok(universe.residual_uncertainty.value <= 1);
  });
  it("explicitates the unknown universe", () => {
    assert.ok(universe.unknown_universe.length >= 8);
    assert.ok(universe.unknown_universe.every((u) => u.id.startsWith("UNK-")));
  });
});

describe("runtime assertions", () => {
  it("holds release and Nurse-PaLM operational claim", () => {
    const r = runtimeAssertions(universe);
    assert.equal(r.ok, true, JSON.stringify(r.failed));
  });
  it("asserts the 12 Drive pages and rejects a report dashboard", () => {
    const r = runtimeAssertions(universe, platform);
    assert.equal(r.ok, true, JSON.stringify(r.failed));
    const poisoned = {
      listing: ["index.html", "app.js"],
      files: { ...platform.files, "index.html": '<html><canvas id="graph"></canvas><h1>Relatório Técnico Final Controlado</h1></html>' },
    };
    const bad = runtimeAssertions(universe, poisoned);
    assert.equal(bad.ok, false);
    assert.ok(bad.failed.some((a) => a.id === "A-NO-REPORT-DASHBOARD"));
  });
});

describe("evaluation science", () => {
  it("matches the golden dataset with precision/recall 1", () => {
    const r = evaluationScience(universe);
    assert.equal(r.ok, true);
    assert.equal(r.precision, 1);
    assert.equal(r.recall, 1);
    assert.equal(r.adversarial.release_attempt, true);
    assert.equal(r.inter_rater.kappa, 1);
    assert.equal(r.drift.psi, 0);
    assert.equal(r.calibration.brier, 0);
    assert.equal(r.synthetic, true);
    assert.equal(r.production_nursepalm, false);
  });
});

describe("software verification", () => {
  it("property-based: mutations cannot sneak a release", () => {
    const r = propertyBased(universe);
    assert.equal(r.ok, true, JSON.stringify(r.trials.filter((t) => !t.blocked)));
  });
  it("contract-testing: valid schema accepted and RELEASED / missing idempotency rejected", () => {
    const r = contractTest(universe, platform);
    assert.equal(r.ok, true, JSON.stringify(r.cases.filter((c) => !c.ok)));
  });
  it("fuzzing: 1000 release attempts never ACCEPT", () => {
    const r = fuzzRelease(universe, 1000, 20260903);
    assert.equal(r.n, 1000);
    assert.equal(r.false_accept, 0);
    assert.equal(r.ok, true);
  });
  it("mutation-testing: drop-unknown, drop-X, inferred-observed and pending-as-ack are killed", () => {
    const r = mutationTesting(universe);
    assert.equal(r.ok, true, JSON.stringify(r.mutants));
  });
  it("model-checking: 64-state release invariant never ALLOW", () => {
    const r = modelCheckReleaseInvariant(universe);
    assert.equal(r.states, 64);
    assert.equal(r.allow, 0);
    assert.equal(r.ok, true);
  });
});

describe("distributed orchestrator", () => {
  it("EVENT → CHECKPOINT → ORCHESTRATOR with idempotency and DLQ", () => {
    const r = orchestrator(universe, [
      { type: "site.materialize", payload: { v: 1 }, idempotency_key: "k1" },
      { type: "site.materialize", payload: { v: 1 }, idempotency_key: "k1" },
      { type: "release.request", payload: {}, idempotency_key: "r1" },
      { type: "ack.claim", payload: { from: "PENDING" }, idempotency_key: "a1" },
    ]);
    assert.equal(r.pattern, "EVENT → CHECKPOINT → ORCHESTRATOR");
    assert.equal(r.acked, 1);
    assert.ok(r.dlq >= 2);
    assert.ok(r.log.some((l) => l.result === "duplicate-suppressed"));
    assert.equal(r.saga.release, "compensated");
    assert.equal(r.retries.max, 3);
  });
  it("retries transient work then DLQ after max attempts", () => {
    const ok = orchestrator(universe, [{ type: "transient.work", payload: { fail_until: 2 }, idempotency_key: "t-ok" }]);
    assert.equal(ok.acked, 1);
    assert.ok(ok.log.filter((l) => l.result === "retry").length >= 2);
    const dead = orchestrator(universe, [{ type: "transient.work", payload: { fail_until: 9 }, idempotency_key: "t-dlq" }]);
    assert.equal(dead.acked, 0);
    assert.equal(dead.dlq, 1);
    assert.ok(dead.log.some((l) => l.result === "dlq-after-retries"));
  });
});

describe("CI gates", () => {
  it("passes the defined gate set without releasing", async () => {
    const ontology = readFileSync(join(gatePub, "graph/ontology.ttl"), "utf8");
    const r = await runGates(universe, { platform, ontology });
    assert.equal(r.ok, true, JSON.stringify(r.failed));
    assert.equal(r.release, "HOLD / NOT_RELEASED");
    assert.equal(r.starts_at, "policy-as-code");
    assert.deepEqual(r.cascade.map((g) => g.id), CASCADE);
    assert.ok(r.gates.every((g) => g.ok && g.status === "PASS"));
    assert.equal(r.verification.fuzz.n, 1000);
    assert.equal(r.verification.fuzz.false_accept, 0);
    assert.equal(r.verification.model.states, 64);
    assert.equal(r.verification.shacl.ok, true);
    assert.equal(r.orchestrator.acked >= 2, true);
  });
});

describe("cascade root", () => {
  it("starts at policy-as-code and skips every downstream stage on policy fail", async () => {
    const clone = structuredClone(universe);
    clone.unknown_universe = [];
    const r = await runGates(clone);
    assert.equal(r.ok, false);
    assert.equal(r.starts_at, "policy-as-code");
    assert.equal(r.cascade[0].id, "policy-as-code");
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.cascade.slice(1).every((s) => s.status === "SKIPPED"));
    assert.equal(r.receipts_n, 0);
  });
  it("does not emit automatic evidence unless the cascade reached that stage", async () => {
    const clone = structuredClone(universe);
    clone.baseline.release = "RELEASED";
    const r = await runGates(clone);
    assert.equal(r.ok, false);
    const evidence = r.cascade.find((s) => s.id === "automatic-evidence");
    assert.ok(evidence.status === "SKIPPED" || evidence.status === "FAIL");
  });
});

describe("runtime frontend", () => {
  it("ships the platform pages and not the control-room graph UI", () => {
    const index = platform.files["index.html"];
    assert.match(index, /Calculadoras de Enfermagem/);
    assert.equal(index.includes('id="graph"'), false);
    assert.equal(index.includes("Reexecutar cascata"), false);
    assert.equal(index.includes("orquestrador"), false);
    for (const p of RUNTIME_PAGES) {
      const html = platform.files[p];
      assert.ok(html.includes("<main"), p);
      assert.equal(html.includes('canvas id="graph"'), false, p);
    }
    assert.equal(platform.listing.includes("app.js"), false);
    const firebase = JSON.parse(readFileSync(join(root, "../../firebase.json"), "utf8"));
    assert.equal(firebase.hosting.public, "reference-website");
    assert.ok(firebase.hosting.ignore.includes("cko-relatorio-tecnico-final.html"));
    assert.ok(firebase.hosting.ignore.includes("grafo-clinico.html"));
  });
  it("ships calculator and library runtimes plus JS engines", () => {
    const plat = validateToolLibrarySchema(platform);
    assert.equal(plat.ok, true, plat.errors.join("; "));
    for (const p of TOOL_RUNTIME_CANARIES) {
      assert.ok(platform.toolLibrary.tool_canaries.includes(p), p);
    }
    for (const p of LIBRARY_RUNTIME_CANARIES) {
      assert.ok(platform.toolLibrary.library_canaries.includes(p), p);
    }
    for (const p of TOOL_ENGINE_LIBS) {
      assert.ok(platform.toolLibrary.engine_libraries.includes(p), p);
    }
    const aldrete = platform.files["aldrete.html"];
    assert.match(aldrete, /btnCalcular/);
    assert.match(aldrete, /scoreValor/);
    assert.match(platform.files["imc.html"], /calcularIMC/);
    assert.match(platform.files["gotejamento.html"], /calcularGotejamento/);
    assert.match(platform.files["biblioteca.html"], /biblioteca/i);
    assert.ok(platform.toolLibrary.biblioteca_articles_n >= 1);
    const r = runtimeAssertions(universe, platform);
    assert.equal(r.ok, true, JSON.stringify(r.failed));
    assert.ok(r.asserts.some((a) => a.id === "A-TOOL-RUNTIME" && a.ok));
    assert.ok(r.asserts.some((a) => a.id === "A-LIBRARY-RUNTIME" && a.ok));
    const g = inspectCalenfGovernance(platform.governance);
    assert.equal(g.ok, true, JSON.stringify(g.denials));
    assert.equal(platform.governance.nursePalm.operational, "NOT_ASSERTED");
    assert.equal(platform.governance.digitalTwin.observed, false);
    assert.equal(platform.governance.agentic.operational, "NOT_ASSERTED");
    assert.equal(platform.governance.agentic.independence, "maker!=checker!=auditor");
    assert.equal(platform.governance.layerCount, 44);
    assert.equal(platform.governance.pageCount, 12);
    assert.ok(platform.governance.nodes.some((n) => n.id === "B1"));
    assert.equal(platform.governance.evidence_chain.id, "CKO-MD-TO-FRONTEND-1.0.0");
    assert.equal(platform.governance.master_data.fields_classified, 2496);
    assert.equal(platform.governance.normative.bindings_classified, 10913);
    assert.equal(platform.governance.evidence_chain.materialized_field_bindings, false);
    assert.equal(platform.toolLibrary.structure, "calenf");
  });
  it("materializes every documented PDF and directory pendency without mutating Drive or closing B9", () => {
    const r = inspectPendencies(pendencies, driveImmutable);
    assert.equal(r.ok, true, JSON.stringify(r.denials));
    const schema = validatePendenciesSchema(platform);
    assert.equal(schema.ok, true, schema.errors.join("; "));
    assert.equal(pendencies.mutate_drive, false);
    assert.equal(pendencies.closes_b9, false);
    assert.equal(pendencies.items.filter((i) => i.kind === "locale-cell").length, 360);
    const byId = Object.fromEntries(pendencies.items.map((i) => [i.id, i]));
    assert.equal(byId["PEND-PDF-HOLDS-BUCKET"].count, 211);
    assert.equal(byId["PEND-PDF-FINDINGS-BUCKET"].count, 313);
    assert.equal(byId["PEND-PDF-REPERF-BUCKET"].count, 201);
    assert.equal(byId["PEND-PDF-OUTBOX-BUCKET"].count, 296);
    assert.equal(byId["PEND-PDF-RIGHTS-BUCKET"].count, 13);
    assert.ok(byId["PEND-BLOCK-B9"]);
    assert.ok(byId["PEND-DIR-SITEMAP"]);
    assert.ok(driveImmutable.files.length >= 10);
    assert.equal(existsSync(join(site, "sitemap.xml")), true);
    assert.equal(existsSync(join(site, "braden.html")), true);
    assert.equal(existsSync(join(site, "berg.html")), true);
    assert.equal(existsSync(join(site, "data/schemas/tool.schema.json")), true);
    assert.equal(existsSync(join(site, "js/nurse-palm.js")), true);
    assert.equal(existsSync(join(site, "js/knowledge-graph.js")), true);
    const rt = runtimeAssertions(universe, platform);
    assert.ok(rt.asserts.some((a) => a.id === "A-PENDENCIES-EXPLICIT" && a.ok));
    assert.ok(rt.asserts.some((a) => a.id === "A-DRIVE-IMMUTABLE" && a.ok));
  });
  it("fails at policy-as-code if the pendency ledger is dropped", async () => {
    const broken = { ...platform, pendencies: { root: "policy-as-code", mutate_drive: false, closes_b9: false, items: [] } };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "PENDENCIES_EXPLICIT"));
    assert.ok(r.cascade.slice(1).every((s) => s.status === "SKIPPED"));
  });
  it("fails at policy-as-code if tool runtimes disappear", async () => {
    const broken = {
      ...platform,
      toolLibrary: { ...platform.toolLibrary, tool_canaries: [], library_canaries: [], engine_libraries: [] },
    };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].id, "policy-as-code");
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "TOOL_RUNTIME_PRESENT"));
    assert.ok(r.cascade.slice(1).every((s) => s.status === "SKIPPED"));
  });
  it("fails at policy-as-code if the report dashboard returns, skipping the rest", async () => {
    const poisoned = {
      listing: ["index.html", "app.js"],
      files: { ...platform.files, "index.html": '<html><canvas id="graph"></canvas><h1>Relatório Técnico Final Controlado</h1></html>' },
    };
    const r = await runGates(universe, { platform: poisoned });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].id, "policy-as-code");
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.cascade.slice(1).every((s) => s.status === "SKIPPED"));
  });
});

describe("platform remediations without Drive mutation", () => {
  it("parses ASA tool-config regenerated from data/tools JSON", () => {
    const html = readFileSync(join(site, "asa.html"), "utf8");
    const match = html.match(/<script[^>]*id="tool-config"[^>]*>([\s\S]*?)<\/script>/);
    assert.ok(match, "asa.html missing #tool-config");
    const cfg = JSON.parse(match[1].replace(/\\u003c/g, "<"));
    assert.equal(cfg.slug, "asa");
    assert.ok(cfg.calculator && Array.isArray(cfg.calculator.inputs));
    const cfgAt = html.lastIndexOf('id="tool-config"');
    assert.ok(cfgAt > html.lastIndexOf("renderizarForm()"));
    assert.match(html, /<\\\/script>\s*<\/body><\/html>`/);
  });
  it("keeps da/uk/zh i18n as HOLD scaffolds off the language selector", () => {
    for (const locale of ["da", "uk", "zh"]) {
      const path = join(site, "i18n", `${locale}.json`);
      assert.equal(existsSync(path), true, `${locale}.json missing`);
      const body = JSON.parse(readFileSync(path, "utf8"));
      assert.equal(body._meta.status, "HOLD_TRANSLATION_REQUIRED");
      assert.equal(body._meta.activate_in_selector, false);
      assert.equal(body._meta.release, "HOLD / NOT_RELEASED");
    }
    const selector = readFileSync(join(site, "js/lang-selector.js"), "utf8");
    const codesMatch = selector.match(/var ALL_LANG_CODES = (\[[^\]]+\])/);
    assert.ok(codesMatch, "ALL_LANG_CODES missing");
    const codes = JSON.parse(codesMatch[1]);
    assert.equal(codes.includes("da"), false);
    assert.equal(codes.includes("uk"), false);
    assert.equal(codes.includes("zh"), false);
    assert.equal(codes.includes("zh-CN"), true);
    const byId = Object.fromEntries(pendencies.items.map((i) => [i.id, i]));
    assert.equal(byId["PEND-DIR-I18N-da"].status, "CREATED_IN_RUNTIME_HOLD");
    assert.equal(byId["PEND-DIR-I18N-uk"].status, "CREATED_IN_RUNTIME_HOLD");
    assert.equal(byId["PEND-DIR-I18N-zh"].status, "CREATED_IN_RUNTIME_HOLD");
  });
  it("resolves slug aliases to calculator HTML instead of redirects", () => {
    const bySlug = Object.fromEntries(toolLibrary.tools.map((t) => [t.slug, t]));
    assert.equal(bySlug["escala-de-braden"].html, "braden.html");
    assert.equal(bySlug["escala-de-glasgow"].html, "glasgow.html");
    assert.equal(bySlug["escala-de-morse"].html, "morse.html");
    assert.equal(bySlug["escala-de-braden"].has_calc_runtime, true);
    assert.equal(bySlug["calculo-rescisao"].has_calc_runtime, true);
    assert.equal(toolLibrary.tools_with_calc_runtime, toolLibrary.tools_n);
  });
  it("ships the 44 classified horizontal layers from the PDF closure onto the CALENF site", () => {
    assert.equal(CANONICAL_LAYER_IDS.length, 44);
    assert.deepEqual(layers.layers.map((l) => l.id), CANONICAL_LAYER_IDS);
    assert.equal(layers.id, "CKO-44-LAYER-SITE-1.0.0");
    assert.equal(layers.count, 44);
    assert.equal(layers.gold, "44/44");
    assert.match(layers.release, /NOT_RELEASED/);
    assert.equal(layers.published, false);
    assert.equal(layers.operational, "NOT_ASSERTED");
    const inspected = inspectLayers(layers, platform.files["ecossistema.html"]);
    assert.equal(inspected.ok, true, JSON.stringify(inspected.denials));
    for (const layer of layers.layers) {
      assert.equal(layer.present, true, layer.id);
      assert.equal(layer.zip_verified, true, layer.id);
      assert.match(layer.release, /NOT_RELEASED/);
      assert.equal(existsSync(join(site, "data/cko/layers", layer.id, "package.zip")), true, layer.id);
      assert.equal(existsSync(join(site, "data/cko/layers", layer.id, "package", "FINAL_MANIFEST.json")), true, layer.id);
      assert.equal(existsSync(join(site, "camadas", layer.id, "index.html")), true, layer.id);
      assert.ok(String(layer.href).includes(`/camadas/${layer.id}`), layer.id);
      assert.ok(layer.runtime_paths.length >= 1, layer.id);
    }
    assert.equal(layers.zip_verified_n, 44);
    const snapshot = JSON.parse(readFileSync(join(site, "data/cko/snapshot-index.json"), "utf8"));
    assert.equal(snapshot.file_count, 449);
    assert.equal(snapshot.gold, 449);
    assert.equal(existsSync(join(site, "camadas", "index.html")), true);
    const pub = layers.layers.find((l) => l.id === "LYR-PUB-001");
    assert.equal(pub.published, false);
    assert.equal(layers.governed_by.graph, "js/knowledge-graph.js");
    assert.equal(layers.governed_by.twin, "B5");
    assert.equal(layers.governed_by.agentic, "B1");
    assert.equal(layers.governed_by.nursePalm, "B10");
    assert.equal(layers.governed_by.master_data, "CKO-MD");
    assert.equal(layers.governed_by.regulatory, "CKO-REG");
    assert.equal(layers.master_data_to_frontend.id, "CKO-MD-TO-FRONTEND-1.0.0");
    const learn = layers.layers.find((l) => l.id === "LYR-LEARN-001");
    assert.equal(learn.semantic, "learning");
    assert.equal(learn.master_data, "CKO-MD");
    assert.equal(learn.evidence.no_fact_without_evidence, true);
    const layerNodes = platform.governance.nodes.filter((n) => n.type === "LayerRuntime");
    assert.equal(layerNodes.length, 44);
    assert.ok(platform.governance.edges.some((e) => e[0] === "LAYER-LYR-CLIN-CALC-001" && e[1] === "B9" && e[2] === "fanIn"));
    assert.ok(platform.governance.edges.some((e) => e[0] === "LAYER-LYR-LEARN-001" && e[1] === "SEM-LEARN" && e[2] === "instanceOf"));
    assert.ok(platform.governance.edges.some((e) => e[0] === "LAYER-CKO-REG" && e[1] === "LAYER-CKO-MD" && e[2] === "derivedFrom"));
    assert.ok(platform.governance.edges.some((e) => e[0] === "PAGE-index" && e[1] === "LAYER-CKO-MD" && e[2] === "derivedFrom"));
    assert.ok(platform.governance.edges.some((e) => e[0] === "PAGE-index" && e[1] === "EVD-PAGE-index" && e[2] === "hasEvidence"));
    const eco = platform.files["ecossistema.html"];
    assert.match(eco, /44\/44/);
    assert.match(eco, /HOLD \/ NOT_RELEASED/);
    assert.match(eco, /IA agêntica/);
    assert.match(eco, /Nurse-PaLM/);
    assert.match(eco, /digital twin/i);
    assert.match(eco, /cko-md-norm-evidence/);
    assert.match(eco, /2496/);
    assert.match(eco, /10913/);
    assert.match(eco, /\/camadas\//);
    assert.match(eco, /cko-assurance-cascade/);
    assert.match(eco, /policy-as-code/);
    assert.match(eco, /\/data\/cko\/cascade\//);
    assert.match(platform.files["index.html"], /data-cko-md="CKO-MD"/);
    assert.match(platform.files["index.html"], /data-cko-reg="CKO-REG"/);
    assert.match(platform.files["aldrete.html"], /data-cko-evidence="HOLD"/);
    assert.equal(eco.includes('id="graph"'), false);
    const rt = runtimeAssertions(universe, platform);
    assert.ok(rt.asserts.some((a) => a.id === "A-LAYERS-44" && a.ok));
    assert.ok(rt.asserts.some((a) => a.id === "A-LAYER-PUB-HOLD" && a.ok));
    assert.ok(rt.asserts.some((a) => a.id === "A-CALENF-AGENTIC" && a.ok));
    assert.ok(rt.asserts.some((a) => a.id === "A-MD-NORM-EVIDENCE" && a.ok));
  });
  it("fails at policy-as-code if the 44 layers disappear", async () => {
    const broken = { ...platform, layers: undefined };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].id, "policy-as-code");
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "LAYERS_44_PRESENT"));
    assert.ok(r.cascade.slice(1).every((s) => s.status === "SKIPPED"));
  });
  it("fails at policy-as-code if agentic runtime claims operational", async () => {
    const broken = {
      ...platform,
      governance: {
        ...platform.governance,
        agentic: { ...platform.governance.agentic, operational: "ASSERTED" },
      },
    };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].id, "policy-as-code");
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "AGENTIC_GOVERNS_RUNTIME"));
    assert.ok(r.cascade.slice(1).every((s) => s.status === "SKIPPED"));
  });
  it("fails at policy-as-code if graph/twin/agentic/Nurse-PaLM bindings drop", async () => {
    const broken = {
      ...platform,
      layers: { ...layers, governed_by: { graph: "missing" } },
    };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "LAYERS_44_PRESENT"));
  });
  it("fails at policy-as-code if MD→norma→evidência stamps drop from the frontend", async () => {
    const broken = {
      ...platform,
      files: { ...platform.files, "index.html": platform.files["index.html"].replace(/data-cko-md="CKO-MD"/, "") },
    };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "MD_NORMS_EVIDENCE_CHAIN"));
  });
  it("fails at policy-as-code if master-data/norm chain is dropped from governance", async () => {
    const broken = {
      ...platform,
      governance: { ...platform.governance, evidence_chain: undefined, master_data: undefined, normative: undefined },
    };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "MD_NORMS_EVIDENCE_CHAIN"));
  });
});

describe("knowledge representation", () => {
  it("validates SHACL Block/Unknown/Release/RuntimePage shapes", () => {
    const r = validateShacl(universe, platform);
    assert.equal(r.ok, true, r.violations.join("; "));
    const released = structuredClone(universe);
    released.blocks.find((b) => b.id === "B9").release = "RELEASED";
    assert.equal(validateShacl(released).ok, false);
  });
  it("keeps a temporal graph with B9 open valid_to", () => {
    const r = temporalGraph(universe);
    assert.equal(r.ok, true);
    assert.equal(r.as_of, "2026-09-02");
    assert.equal(r.b9_open_interval, true);
  });
  it("projects RDF triples and requires OWL constructs in the ontology", () => {
    const ttl = readFileSync(join(gatePub, "graph/ontology.ttl"), "utf8");
    const r = projectRdf(universe, ttl);
    assert.equal(r.ok, true);
    assert.ok(r.tripleCount > 0);
    assert.equal(r.owlOk, true);
    assert.match(ttl, /owl:TransitiveProperty/);
    assert.match(ttl, /owl:inverseOf/);
  });
  it("reasons fan-in to HOLD B9 as cannot-release", () => {
    const r = reasonGraph(universe);
    assert.equal(r.ok, true);
    assert.equal(r.inferred_n, 12);
  });
});

describe("design system runtime render", () => {
  const dsPath = join(site, "data/cko/design-system.json");
  it("ships a fail-closed catalog with 37 components, 21 templates, 4 themes and 44 slots", () => {
    assert.equal(existsSync(dsPath), true);
    const ds = JSON.parse(readFileSync(dsPath, "utf8"));
    assert.equal(ds.id, "CKO-DS-RUNTIME-1.0.0");
    assert.equal(ds.layer, "LYR-DS-001");
    assert.match(ds.release, /NOT_RELEASED/);
    assert.equal(ds.published, false);
    assert.equal(ds.operational, "NOT_ASSERTED");
    assert.equal(ds.inventory.components, 37);
    assert.equal(ds.inventory.templates, 21);
    assert.equal(ds.inventory.themes, 4);
    assert.equal(ds.inventory.theme_slots, 44);
    assert.equal(ds.components.length, 37);
    assert.equal(ds.templates.length, 21);
    assert.equal(ds.themes.length, 4);
    assert.equal(ds.theme_slots.length, 44);
    assert.equal(ds.accepted_authority, "ADR-DS-001");
    assert.equal(ds.holds.length, 4);
    assert.equal(existsSync(join(site, "css/cko-ds.css")), true);
    assert.equal(existsSync(join(site, "css/cko-ds-tokens.css")), true);
    assert.equal(existsSync(join(site, "js/cko-ds-render.js")), true);
    const tokens = readFileSync(join(site, "css/cko-ds-tokens.css"), "utf8");
    assert.match(tokens, /--cko-navy-900:\s*#1a3e74/i);
    assert.match(tokens, /--cko-slot-01:/);
    assert.match(tokens, /--cko-slot-44:/);
    assert.equal(ds.templates_implemented_n, 11);
    assert.equal(ds.templates.filter((t) => t.status === "implemented").length, 11);
    assert.ok(ds.templates.every((t) => t.status === "implemented" || t.status === "wireframe"));
    assert.ok(ds.templates.every((t) => t.governed_by?.contract === "POLICY_MASTER_CONTRACT"));
    assert.equal(ds.templates.find((t) => t.id === "tool").governed_by.policy, "CKO-POL-UT-001");
    assert.equal(ds.templates.find((t) => t.id === "scale").governed_by.policy, "CKO-POL-UT-001");
    assert.equal(ds.template_governance.status, "BOUND_HOLD");
    const tplGov = inspectTemplateGovernance(ds, universalToolPolicy);
    assert.equal(tplGov.ok, true, JSON.stringify(tplGov.denials));
    assert.match(ds.refinement, /1\.2\.0-HOLD/);
    assert.equal(ds.identity_manual.version, "v10");
    assert.equal(ds.identity_manual.release_allowed, false);
    assert.match(tokens, /--navy:\s*var\(--cko-navy-900\)/);
    assert.match(tokens, /--navy-light:\s*var\(--cko-navy-700\)/);
    assert.match(tokens, /--navy-dark:\s*var\(--cko-navy-800\)/);
    const renderer = readFileSync(join(site, "js/cko-ds-render.js"), "utf8");
    assert.match(renderer, /data-cko-ds-render/);
    assert.match(renderer, /NOT_ASSERTED/);
    const dsLayer = layers.layers.find((l) => l.id === "LYR-DS-001");
    assert.ok(dsLayer.runtime_paths.includes("css/cko-ds.css"));
    assert.ok(dsLayer.runtime_paths.includes("js/cko-ds-render.js"));
    assert.ok(dsLayer.runtime_paths.includes("data/cko/design-system.json"));
    const dsPage = readFileSync(join(site, "camadas/LYR-DS-001/index.html"), "utf8");
    assert.match(dsPage, /data-cko-ds-render="catalog"/);
    assert.match(dsPage, /cko-ds-render\.js/);
    const uiPage = readFileSync(join(site, "camadas/LYR-UI-001/index.html"), "utf8");
    assert.match(uiPage, /data-cko-ds-render="states"/);
    const hub = readFileSync(join(site, "camadas/index.html"), "utf8");
    assert.match(hub, /data-cko-ds-render="layers"/);
    assert.match(readFileSync(join(site, "global-styles.css"), "utf8"), /cko-ds-tokens\.css/);
  });
  it("starts the catalog at policy-as-code and skips nothing in the cascade", () => {
    assert.equal(designSystem.root, "policy-as-code");
    assert.equal(designSystem.starts_at, "policy-as-code");
    assert.deepEqual(designSystem.cascade, CASCADE);
    assert.equal(designSystem.release_allowed, false);
    const r = inspectDesignSystem(designSystem);
    assert.equal(r.ok, true, JSON.stringify(r.denials));
    assert.match(readFileSync(join(site, "js/cko-ds-render.js"), "utf8"), /cko-ds-cascade/);
  });
  it("fails at policy-as-code if the design system skips the cascade root", async () => {
    const broken = { ...platform, designSystem: { ...designSystem, root: "runtime-assertions", starts_at: "runtime-assertions" } };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].id, "policy-as-code");
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "DS_STARTS_AT_POLICY"));
    assert.ok(r.cascade.slice(1).every((s) => s.status === "SKIPPED"));
  });
});

describe("CKO-POL-UT-001 Universal Tool Policy", () => {
  it("encodes v1.3.0 as HOLD policy-as-code with 98 UTC controls none implemented", () => {
    const r = inspectUniversalToolPolicy(universalToolPolicy);
    assert.equal(r.ok, true, JSON.stringify(r.denials));
    assert.equal(universalToolPolicy.id, UT_POLICY_ID);
    assert.equal(universalToolPolicy.document_id, UT_DOCUMENT_ID);
    assert.equal(universalToolPolicy.control_count, UT_CONTROL_N);
    assert.equal(universalToolPolicy.controls.length, UT_CONTROL_N);
    assert.equal(universalToolPolicy.implemented_n, 0);
    assert.equal(universalToolPolicy.implantado, false);
    assert.equal(universalToolPolicy.assured, false);
    assert.equal(universalToolPolicy.md_gate, UT_MD_GATE);
    assert.equal(universalToolPolicy.clinical_calculators, "PAUSED");
    assert.equal(universalToolPolicy.scales_scores, "PAUSED");
    assert.equal(universalToolPolicy.abnt.nbr_6023.edition, "2025");
    assert.equal(universalToolPolicy.evaluation.verdict, "DOCUMENTADO_HOLD_NOT_IMPLEMENTED");
    assert.equal(universalToolPolicy.evaluation.clinical_promotion, "DENIED");
    assert.equal(universalToolPolicy.version_lineage.status, "VERSION_DRIFT_HOLD");
    assert.equal(universalToolPolicy.starts_at, "policy-as-code");
    assert.equal(universalToolPolicy.parent, POLICY_MASTER_ID);
    assert.equal(universalToolPolicy.specializes, POLICY_MASTER_ID);
    assert.equal(universalToolPolicy.contract.field_count, 28);
    assert.deepEqual(Object.keys(universalToolPolicy.contract.fields), POLICY_MASTER_FIELDS);
    assert.equal(universalToolPolicy.template_governance.status, "BOUND_HOLD");
    assert.equal(universalToolPolicy.template_governance.implantado, false);
    assert.ok(["tool", "calculator", "scale"].every((id) => universalToolPolicy.template_governance.templates.some((t) => t.id === id)));
    assert.ok(universalToolPolicy.controls.every((c) => c.implemented === false && c.status === "DOCUMENTADO_HOLD"));
  });
  it("fails at policy-as-code if calculators are claimed PASS or any UTC is implemented", async () => {
    const broken = {
      ...platform,
      universalToolPolicy: {
        ...universalToolPolicy,
        clinical_calculators: "PASS",
        implantado: true,
        controls: universalToolPolicy.controls.map((c, i) => (i === 0 ? { ...c, implemented: true, status: "PASS" } : c)),
      },
    };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "UT_POLICY_HOLD"));
    assert.ok(r.cascade.slice(1).every((s) => s.status === "SKIPPED"));
  });
  it("renders the evaluation from JSON on the cascade page", () => {
    assert.match(readFileSync(join(site, "js/cko-ds-render.js"), "utf8"), /universal-tool/);
    assert.match(readFileSync(join(site, "data/cko/cascade/index.html"), "utf8"), /data-cko-ds-render="universal-tool"/);
  });
  it("fails at policy-as-code if UT skips POLICY_MASTER_CONTRACT", async () => {
    const broken = {
      ...platform,
      universalToolPolicy: {
        ...universalToolPolicy,
        parent: "POL-CKO-FAIL-CLOSED-1.0.0",
        specializes: undefined,
        template_governance: { ...universalToolPolicy.template_governance, status: "UNBOUND" },
      },
    };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "UT_POLICY_HOLD" || d.id === "TEMPLATE_POLICY_HOLD"));
  });
});

describe("POLICY_MASTER_CONTRACT", () => {
  it("freezes 28 fields as a HOLD template not ACTIVE", () => {
    const r = inspectPolicyMaster(policyMaster);
    assert.equal(r.ok, true, JSON.stringify(r.denials));
    assert.equal(policyMaster.id, POLICY_MASTER_ID);
    assert.equal(policyMaster.field_count, POLICY_MASTER_FIELD_N);
    assert.equal(policyMaster.fields.length, POLICY_MASTER_FIELD_N);
    assert.deepEqual(policyMaster.fields.map((f) => f.id), POLICY_MASTER_FIELDS);
    assert.ok(policyMaster.fields.every((f) => f.meaning && f.question && f.base_kind && f.implemented === false));
    assert.equal(policyMaster.principles.length, 20);
    assert.equal(policyMaster.evaluation.verdict, "ACCEPTED_FROZEN_HOLD");
    assert.equal(policyMaster.status, "CONTROLLED_TEMPLATE_HOLD");
    assert.equal(policyMaster.active, false);
    assert.equal(policyMaster.frozen, true);
    assert.equal(policyMaster.new_architectural_root, false);
  });
  it("fails at policy-as-code if the master is marked ACTIVE", async () => {
    const broken = { ...platform, policyMaster: { ...policyMaster, active: true, status: "ACTIVE" } };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "POLICY_MASTER_HOLD"));
  });
});

describe("Visual Asset System", () => {
  it("binds discovery/share/content to existing layers without a 45th root", () => {
    const r = inspectVisualAssetPolicy(visualAssetPolicy);
    assert.equal(r.ok, true, JSON.stringify(r.denials));
    assert.equal(visualAssetPolicy.id, VAS_POLICY_ID);
    assert.equal(visualAssetPolicy.families.length, VAS_FAMILY_N);
    assert.equal(visualAssetPolicy.internal_policies.length, VAS_INTERNAL_POLICY_N);
    assert.equal(visualAssetPolicy.new_architectural_root, false);
    assert.equal(visualAssetPolicy.one_image_per_page, false);
    assert.equal(visualAssetPolicy.generator.operational, "NOT_ASSERTED");
    assert.equal(visualAssetPolicy.document_projections.docx.files_generated, false);
    assert.equal(visualAssetPolicy.dimensions.og.width, 1200);
    assert.equal(visualAssetPolicy.dimensions.og.height, 630);
    assert.equal(visualAssetPolicy.dimensions.linkedin.height, 627);
  });
  it("fails at policy-as-code if VAS claims a 45th layer or generated Word files", async () => {
    const broken = {
      ...platform,
      visualAssetPolicy: {
        ...visualAssetPolicy,
        new_architectural_root: true,
        document_projections: { ...visualAssetPolicy.document_projections, docx: { files_generated: true } },
      },
    };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "VAS_HOLD"));
  });
  it("renders master and VAS from JSON on the cascade page", () => {
    const html = readFileSync(join(site, "data/cko/cascade/index.html"), "utf8");
    assert.match(html, /data-cko-ds-render="policy-master"/);
    assert.match(html, /data-cko-ds-render="visual-assets"/);
    assert.match(readFileSync(join(site, "js/cko-ds-render.js"), "utf8"), /renderVisualAssets/);
  });
});

describe("platform closure hold policies", () => {
  it("specializes the nine human holds onto POLICY_MASTER_CONTRACT", () => {
    const r = inspectPlatformClosure(platformClosure, humanDecisions);
    assert.equal(r.ok, true, JSON.stringify(r.denials));
    assert.equal(platformClosure.id, CLOSURE_POLICY_ID);
    assert.equal(platformClosure.document_id, CLOSURE_DOCUMENT_ID);
    assert.equal(platformClosure.hold_count, HOLD_POLICY_N);
    assert.equal(platformClosure.holds.length, HOLD_POLICY_N);
    assert.equal(platformClosure.active, false);
    assert.equal(platformClosure.release_allowed, false);
    assert.equal(platformClosure.specializes, POLICY_MASTER_ID);
    assert.ok(platformClosure.holds.every((h) => h.contract.field_count === 28 && h.specializes === POLICY_MASTER_ID && h.active === false));
    assert.ok(humanDecisions.items.every((item) => platformClosure.holds.some((h) => h.hold_id === item.id && h.id === item.policy_id)));
  });
  it("fails at policy-as-code if a hold policy is marked ACTIVE", async () => {
    const brokenHolds = platformClosure.holds.map((h, i) => (i === 0 ? { ...h, active: true, implantado: true } : h));
    const broken = { ...platform, platformClosure: { ...platformClosure, holds: brokenHolds } };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "PLATFORM_CLOSURE_HOLD"));
  });
  it("renders the closure catalog on cascade and holds pages", () => {
    assert.match(readFileSync(join(site, "data/cko/cascade/index.html"), "utf8"), /data-cko-ds-render="platform-closure"/);
    assert.match(readFileSync(join(site, "cko-holds.html"), "utf8"), /data-cko-ds-render="platform-closure"/);
    assert.match(readFileSync(join(site, "js/cko-ds-render.js"), "utf8"), /renderPlatformClosure/);
    assert.match(readFileSync(join(site, "cko-holds.html"), "utf8"), /data-cko-ds-render="human-holds"/);
  });
});

describe("layer and extraction hold policies", () => {
  it("specializes all 44 layers onto POLICY_MASTER_CONTRACT", () => {
    const r = inspectLayerPolicies(layerPolicies, layers);
    assert.equal(r.ok, true, JSON.stringify(r.denials));
    assert.equal(layerPolicies.id, LAYER_CATALOG_ID);
    assert.equal(layerPolicies.document_id, LAYER_DOCUMENT_ID);
    assert.equal(layerPolicies.layer_count, LAYER_POLICY_N);
    assert.equal(layerPolicies.layers.length, LAYER_POLICY_N);
    assert.equal(layerPolicies.active, false);
    assert.equal(layerPolicies.release_allowed, false);
    assert.ok(layerPolicies.layers.every((l) => l.contract.field_count === 28 && l.specializes === POLICY_MASTER_ID && l.active === false));
    assert.ok(layers.layers.every((l) => l.policy_id && l.specializes === POLICY_MASTER_ID));
    const calc = layerPolicies.layers.find((l) => l.layer_id === "LYR-CLIN-CALC-001");
    const scale = layerPolicies.layers.find((l) => l.layer_id === "LYR-CLIN-SCALE-001");
    assert.equal(calc.clinical_state, "PAUSED");
    assert.equal(scale.clinical_state, "PAUSED");
  });
  it("fails at policy-as-code if a layer policy is marked ACTIVE", async () => {
    const brokenLayers = layerPolicies.layers.map((l, i) => (i === 0 ? { ...l, active: true, implantado: true } : l));
    const broken = { ...platform, layerPolicies: { ...layerPolicies, layers: brokenLayers } };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "LAYER_POLICY_HOLD"));
  });
  it("creates the extraction catalog that did not exist as policy-as-code", () => {
    const r = inspectExtractionPolicy(extractionPolicy);
    assert.equal(r.ok, true, JSON.stringify(r.denials));
    assert.equal(extractionPolicy.id, EXTRACTION_POLICY_ID);
    assert.equal(extractionPolicy.document_id, EXTRACTION_DOCUMENT_ID);
    assert.equal(extractionPolicy.stream_count, EXTRACTION_STREAM_N);
    assert.equal(extractionPolicy.active, false);
    assert.equal(extractionPolicy.implantado, false);
    assert.equal(extractionPolicy.assured, false);
    const corpus = extractionPolicy.streams.find((s) => s.stream_id === "EXT-REG-CORPUS");
    assert.equal(corpus.count, 0);
    assert.ok(extractionPolicy.streams.every((s) => s.specializes === POLICY_MASTER_ID && s.contract.field_count === 28));
  });
  it("fails at policy-as-code if extraction claims implantado", async () => {
    const broken = { ...platform, extractionPolicy: { ...extractionPolicy, implantado: true, active: true } };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "EXTRACTION_POLICY_HOLD"));
  });
  it("renders layer and extraction catalogs on cascade and holds pages", () => {
    const cascade = readFileSync(join(site, "data/cko/cascade/index.html"), "utf8");
    const holds = readFileSync(join(site, "cko-holds.html"), "utf8");
    assert.match(cascade, /data-cko-ds-render="layer-policies"/);
    assert.match(cascade, /data-cko-ds-render="extraction"/);
    assert.match(holds, /data-cko-ds-render="layer-policies"/);
    assert.match(holds, /data-cko-ds-render="extraction"/);
    assert.match(readFileSync(join(site, "js/cko-ds-render.js"), "utf8"), /renderLayerPolicies/);
    assert.match(readFileSync(join(site, "js/cko-ds-render.js"), "utf8"), /renderExtraction/);
  });
});

describe("API catalog hold", () => {
  it("extracts and binds the nine API families from the shared conversation", () => {
    const r = inspectApiCatalog(apiCatalog);
    assert.equal(r.ok, true, JSON.stringify(r.denials));
    assert.equal(apiCatalog.id, API_CATALOG_ID);
    assert.equal(apiCatalog.document_id, API_DOCUMENT_ID);
    assert.equal(apiCatalog.family_count, API_FAMILY_N);
    assert.equal(apiCatalog.families.length, API_FAMILY_N);
    assert.equal(apiCatalog.endpoint_total, API_ENDPOINT_TOTAL);
    assert.equal(apiCatalog.active, false);
    assert.equal(apiCatalog.release_allowed, false);
    assert.equal(apiCatalog.implantado, false);
    assert.equal(apiCatalog.assured, false);
    assert.equal(apiCatalog.md_reg_complete, false);
    assert.equal(apiCatalog.md_reg_next_task, true);
    assert.ok(apiCatalog.families.every((f) => f.contract.field_count === 28 && f.specializes === POLICY_MASTER_ID && f.active === false));
    const shared = apiCatalog.families.find((f) => f.family_id === "API-SHARED-DEEPSEEK");
    const slugs = (shared.endpoints || []).map((e) => e.slug);
    assert.ok(slugs.includes("cko-deepseek-gateway"));
    assert.ok(slugs.includes("cko-deepseek-regulatory-extract"));
    assert.ok(slugs.includes("cko-deepseek-health"));
    const rest = apiCatalog.families.find((f) => f.family_id === "API-NIS-REST");
    const calc = (rest.endpoints || []).find((e) => String(e.path || "").includes("/calculate"));
    assert.equal(calc.clinical, "PAUSED");
    const next = apiCatalog.families.find((f) => f.family_id === "API-MD-REG-NEXT");
    assert.equal(next.md_reg_complete, false);
  });
  it("fails at policy-as-code if the API catalog is marked ACTIVE or MD/REG complete", async () => {
    const broken = { ...platform, apiCatalog: { ...apiCatalog, active: true, implantado: true, md_reg_complete: true } };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "API_CATALOG_HOLD"));
  });
  it("renders the API catalog on cascade and holds pages", () => {
    const cascade = readFileSync(join(site, "data/cko/cascade/index.html"), "utf8");
    const holds = readFileSync(join(site, "cko-holds.html"), "utf8");
    assert.match(cascade, /data-cko-ds-render="api-catalog"/);
    assert.match(holds, /data-cko-ds-render="api-catalog"/);
    assert.match(readFileSync(join(site, "js/cko-ds-render.js"), "utf8"), /renderApiCatalog/);
  });
});

describe("governed fabric hold", () => {
  it("binds the shared-conversation assurance stack and acquisition APIs", () => {
    const r = inspectGovernedFabric(governedFabric);
    assert.equal(r.ok, true, JSON.stringify(r.denials));
    assert.equal(governedFabric.id, FABRIC_POLICY_ID);
    assert.equal(governedFabric.document_id, FABRIC_DOCUMENT_ID);
    assert.equal(governedFabric.family_count, FABRIC_FAMILY_N);
    assert.equal(governedFabric.families.length, FABRIC_FAMILY_N);
    assert.equal(governedFabric.item_total, FABRIC_ITEM_TOTAL);
    assert.equal(governedFabric.active, false);
    assert.equal(governedFabric.release_allowed, false);
    assert.equal(governedFabric.implantado, false);
    assert.equal(governedFabric.assured, false);
    assert.equal(governedFabric.md_reg_complete, false);
    assert.equal(governedFabric.md_reg_next_task, true);
    assert.equal(governedFabric.source.not, "cko-deepseek-blackboard");
    assert.ok(governedFabric.families.every((f) => f.contract.field_count === 28 && f.specializes === POLICY_MASTER_ID && f.active === false));
    const assure = governedFabric.families.find((f) => f.family_id === "FAB-ASSURE");
    assert.deepEqual((assure.items || []).map((i) => i.id), ASSURE_TECH_IDS);
    const tools = governedFabric.families.find((f) => f.family_id === "FAB-AGENT-TOOL");
    assert.deepEqual((tools.items || []).map((i) => i.id), AGENT_TOOL_IDS);
    const next = governedFabric.families.find((f) => f.family_id === "FAB-MD-REG-NEXT");
    assert.equal(next.md_reg_complete, false);
  });
  it("fails at policy-as-code if the fabric is marked ACTIVE or MD/REG complete", async () => {
    const broken = { ...platform, governedFabric: { ...governedFabric, active: true, implantado: true, md_reg_complete: true } };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "GOVERNED_FABRIC_HOLD"));
  });
  it("renders the fabric on cascade and holds pages", () => {
    const cascade = readFileSync(join(site, "data/cko/cascade/index.html"), "utf8");
    const holds = readFileSync(join(site, "cko-holds.html"), "utf8");
    assert.match(cascade, /data-cko-ds-render="governed-fabric"/);
    assert.match(holds, /data-cko-ds-render="governed-fabric"/);
    assert.match(readFileSync(join(site, "js/cko-ds-render.js"), "utf8"), /renderGovernedFabric/);
  });
});

describe("applied security probes", () => {
  it("denies forged ACK, replay, injection, traversal and prompt injection without a second effect", () => {
    const r = securityOffensive(universe);
    assert.equal(r.ok, true, JSON.stringify(r.probes));
    const ids = r.probes.map((p) => p.id);
    assert.deepEqual(ids, ["FORGED_ACK", "REPLAY", "INJECTION", "PATH_TRAVERSAL", "PROMPT_INJECTION"]);
  });
});

describe("MD/REG as policy through the frontend", () => {
  it("treats CKO-MD + CKO-REG as executable policy-as-code", () => {
    const r = inspectMdRegPolicy(mdRegPolicy);
    assert.equal(r.ok, true, JSON.stringify(r.denials));
    assert.equal(mdRegPolicy.id, MD_REG_POLICY_ID);
    assert.deepEqual(mdRegPolicy.chain, MD_REG_CHAIN);
    assert.equal(mdRegPolicy.release_allowed, false);
    assert.equal(mdRegPolicy.parent, POLICY_MASTER_ID);
    assert.equal(mdRegPolicy.specializes, POLICY_MASTER_ID);
    assert.equal(mdRegPolicy.contract.field_count, 28);
  });
  it("keeps human decisions HOLD_HUMAN_NON_BLOCKING without failing inspect", async () => {
    const human = inspectHumanDecisions(humanDecisions);
    assert.equal(human.ok, true, JSON.stringify(human.denials));
    assert.equal(humanDecisions.status, HOLD_HUMAN_STATUS);
    assert.equal(humanDecisions.blocking_inspect, false);
    const r = await runGates(universe, { platform });
    assert.equal(r.ok, true, JSON.stringify(r.failed));
    assert.equal(r.policy.release_allowed, false);
    assert.ok(r.runtime.asserts.some((a) => a.id === "A-HOLD-HUMAN-NON-BLOCKING" && a.ok));
    assert.equal(humanDecisions.hold_count, HOLD_POLICY_N);
    assert.ok(humanDecisions.items.every((item) => item.policy_id && item.specializes === POLICY_MASTER_ID));
  });
  it("fails inspect only if a human decision is marked blocking", async () => {
    const broken = {
      ...platform,
      humanDecisions: {
        ...humanDecisions,
        items: humanDecisions.items.map((item, i) =>
          i === 0 ? { ...item, blocking_inspect: true } : item
        ),
      },
    };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "HOLD_HUMAN_NON_BLOCKING"));
  });
});

describe("chrome templates", () => {
  it("keeps calculator/tool/institutional templates with slots xor static chrome", () => {
    for (const name of ["calculator.html", "tool.html", "institutional.html"]) {
      const html = readFileSync(join(site, "templates", name), "utf8");
      assert.match(html, /data-cko-slot="chrome"/);
      assert.match(html, /data-cko-slot="hero"/);
      assert.equal(/<nav\b[^>]*(?:tpl-breadcrumb|crumbs)/i.test(html), false, name);
      assert.equal(/<section\b[^>]*class="[^"]*\bhero\b/i.test(html), false, name);
      assert.equal(/<(?:div|header)\b[^>]*tool-header/i.test(html), false, name);
    }
    const gen = readFileSync(join(site, "scripts/generate_tool_page.py"), "utf8");
    assert.match(gen, /data-cko-static="breadcrumb"/);
    assert.match(gen, /data-cko-static="hero"/);
    const shell = readFileSync(join(site, "js/cko-page-shell.js"), "utf8");
    assert.match(shell, /hasStaticHero/);
    assert.match(shell, /data-cko-deduped/);
    const home = readFileSync(join(site, "templates/home.html"), "utf8");
    assert.match(home, /data-cko-static="hero"/);
    const calcTpl = readFileSync(join(site, "calculadora-template.html"), "utf8");
    assert.match(calcTpl, /data-cko-static="breadcrumb"/);
    assert.match(calcTpl, /data-cko-static="hero"/);
  });
  it("keeps Aldrete/IMC with a local H1 in source; shell now prefers the cluster hero", () => {
    for (const name of ["aldrete.html", "imc.html"]) {
      const html = readFileSync(join(site, name), "utf8");
      assert.match(html, /data-cko-slot="hero"/);
      assert.match(html, /<h1\b/);
    }
    const shell = readFileSync(join(site, "js/cko-page-shell.js"), "utf8");
    assert.match(shell, /hideLegacyLocalHeroes/);
    assert.match(shell, /data-cko-legacy-hero/);
    const staticFn = shell.slice(shell.indexOf("function hasStaticHero"), shell.indexOf("function hideLegacyLocalHeroes"));
    assert.equal(staticFn.includes("-card-navy"), false);
    assert.equal(shell.includes("-card-navy"), true);
    const missao = readFileSync(join(site, "missao.html"), "utf8");
    assert.match(missao, /class="crumbs"/);
    assert.match(missao, /<section class="hero"/);
    assert.equal(missao.includes("data-cko-slot="), false);
  });
  it("binds tool/calculator/scale HTML to CKO-POL-UT-001 and POLICY_MASTER_CONTRACT", () => {
    for (const name of ["calculator.html", "tool.html", "scale.html"]) {
      const html = readFileSync(join(site, "templates", name), "utf8");
      assert.match(html, /data-cko-policy="CKO-POL-UT-001"/);
      assert.match(html, /data-cko-contract="POLICY_MASTER_CONTRACT"/);
      assert.match(html, /data-cko-utc="UTC-013 UTC-046"/);
    }
    const specimen = readFileSync(join(site, "escala-padrao.html"), "utf8");
    assert.match(specimen, /data-cko-policy="CKO-POL-UT-001"/);
    assert.match(specimen, /data-cko-contract="POLICY_MASTER_CONTRACT"/);
    for (const name of ["home.html", "institutional.html", "library.html", "content.html"]) {
      const html = readFileSync(join(site, "templates", name), "utf8");
      assert.match(html, /data-cko-contract="POLICY_MASTER_CONTRACT"/);
    }
    const renderer = readFileSync(join(site, "js/cko-ds-render.js"), "utf8");
    assert.match(renderer, /governed_by/);
    assert.match(renderer, /Base normativa/);
  });
  it("fails at policy-as-code if catalog templates lose policy binding", async () => {
    const unbound = designSystem.templates.map((t) => ({ ...t, governed_by: undefined }));
    const broken = {
      ...platform,
      designSystem: { ...designSystem, templates: unbound, template_governance: { contract: "NONE" } },
    };
    const r = await runGates(universe, { platform: broken });
    assert.equal(r.ok, false);
    assert.equal(r.cascade[0].status, "FAIL");
    assert.ok(r.policy.inspect.denials.some((d) => d.id === "TEMPLATE_POLICY_HOLD"));
  });
  it("ships refined scale/library/content templates and gates rating copy", () => {
    for (const name of ["scale.html", "library.html", "content.html"]) {
      const html = readFileSync(join(site, "templates", name), "utf8");
      assert.match(html, /data-cko-slot="chrome"/);
      assert.match(html, /data-cko-slot="hero"/);
    }
    const gen = readFileSync(join(site, "scripts/generate_tool_page.py"), "utf8");
    assert.match(gen, /HOLD-HUMAN-COPY-RATINGS/);
    assert.equal(gen.includes("de 5 estrelas"), false);
    assert.equal(existsSync(join(site, "js/cko-ratings-hold.js")), true);
    const gate = readFileSync(join(site, "js/cko-ratings-hold.js"), "utf8");
    assert.match(gate, /HOLD-HUMAN-COPY-RATINGS/);
    assert.match(readFileSync(join(site, "js/partials-loader.js"), "utf8"), /cko-ratings-hold\.js/);
    const calc = readFileSync(join(site, "camadas/LYR-CLIN-CALC-001/index.html"), "utf8");
    assert.match(calc, /data-cko-ds-render="universal-tool"/);
    const tpl = readFileSync(join(site, "camadas/LYR-PAGE-TPL-001/index.html"), "utf8");
    assert.match(tpl, /data-cko-ds-render="templates"/);
    const holds = readFileSync(join(site, "cko-holds.html"), "utf8");
    assert.match(holds, /data-cko-ds-render="human-holds"/);
    assert.ok(humanDecisions.items.every((item) => item.code_progress && item.next_human));
    assert.ok(humanDecisions.items.every((item) => item.status === "HOLD_HUMAN_NON_BLOCKING"));
  });
  it("ships identity v10 and scale specimen on the standard cluster", () => {
    const identidade = readFileSync(join(site, "cko-identidade.html"), "utf8");
    assert.match(identidade, /data-cko-template="institutional"/);
    assert.match(identidade, /data-cko-page="cko-identidade"/);
    assert.match(identidade, /data-cko-slot="chrome"/);
    assert.match(identidade, /data-cko-slot="hero"/);
    assert.match(identidade, /data-cko-ds-render="manual"/);
    assert.equal(/<style[\s\S]*--navy-light/.test(identidade), false);
    const scale = readFileSync(join(site, "templates/scale.html"), "utf8");
    assert.match(scale, /data-cko-template="scale"/);
    assert.match(scale, /data-cko-scale-items/);
    assert.match(scale, /cko-scale-grid/);
    assert.equal(scale.includes("-card-navy"), false);
    const specimen = readFileSync(join(site, "escala-padrao.html"), "utf8");
    assert.match(specimen, /data-cko-page="escala-padrao"/);
    assert.match(specimen, /data-cko-scale-items/);
    assert.match(specimen, /CKO-POL-UT-001/);
    assert.equal(specimen.includes("-card-navy"), false);
    const renderer = readFileSync(join(site, "js/cko-ds-render.js"), "utf8");
    assert.match(renderer, /renderIdentityManual/);
    assert.match(readFileSync(join(site, "js/cko-scale-standard.js"), "utf8"), /cko-tpl-scale/);
    const catalog = JSON.parse(readFileSync(join(site, "data/cko-shell-pages.json"), "utf8"));
    assert.ok(catalog.pages["cko-identidade"]);
    assert.ok(catalog.pages["escala-padrao"]);
    const dsLayer = readFileSync(join(site, "camadas/LYR-DS-001/index.html"), "utf8");
    assert.match(dsLayer, /global-header-container/);
    assert.match(dsLayer, /cko-identidade\.html/);
  });
});

describe("unpublished platform status page", () => {
  it("ships a Portuguese HOLD status page without claiming ACTIVE or adding a 13th runtime page", () => {
    assert.equal(RUNTIME_PAGES.length, 12);
    assert.equal(RUNTIME_PAGES.includes("cko-estado.html"), false);
    const html = readFileSync(join(site, "cko-estado.html"), "utf8");
    assert.match(html, /não foi publicada/i);
    assert.match(html, /HOLD \/ NOT_RELEASED/);
    assert.match(html, /DOCUMENTADO ≠ IMPLANTADO ≠ ASSURED ≠ PUBLICADO/);
    assert.match(html, /release_allowed: false/);
    assert.match(html, /ainda não existe/i);
    assert.match(html, /não foi publicado/i);
    assert.match(html, /NOT_ASSERTED/);
    assert.equal(/status["']:\s*["']ACTIVE["']/.test(html), false);
    assert.equal(html.includes("implantado: true"), false);
    const home = readFileSync(join(site, "index.html"), "utf8");
    assert.match(home, /cko-estado\.html/);
    assert.match(home, /não publicada/);
    assert.match(readFileSync(join(site, "mapa-do-site.html"), "utf8"), /cko-estado\.html/);
    assert.match(readFileSync(join(site, "ecossistema.html"), "utf8"), /cko-estado\.html/);
    assert.match(readFileSync(join(site, "cko-holds.html"), "utf8"), /cko-estado\.html/);
    assert.match(readFileSync(join(site, "menu-global.html"), "utf8"), /cko-estado\.html/);
    assert.match(readFileSync(join(site, "footer.html"), "utf8"), /cko-estado\.html/);
  });
});

describe("REG universe v1.2.1 Drive successor HOLD", () => {
  const stampPath = join(gatePub, "drive/CKO-REFERENCE-STANDARDS-UNIVERSE-v1.2.1-HOLD.json");
  const freezePath = join(site, "data/cko/layers/LYR-REF-001/package/FINAL_MANIFEST.json");

  it("catalogs the Drive zip without replacing the v1.1.1 freeze or completing MD/REG", () => {
    const stamp = JSON.parse(readFileSync(stampPath, "utf8"));
    const catalog = JSON.parse(readFileSync(join(gatePub, "drive/catalog.json"), "utf8"));
    const freeze = JSON.parse(readFileSync(freezePath, "utf8"));
    const gateLayers = JSON.parse(readFileSync(join(gatePub, "data/layers.json"), "utf8"));
    assert.equal(stamp.release_allowed, false);
    assert.equal(stamp.freeze_replaced, false);
    assert.equal(stamp.md_reg_complete, false);
    assert.equal(stamp.corpus_extracted, false);
    assert.equal(stamp.successor.reference_count, 139);
    assert.equal(stamp.freeze.references, 113);
    assert.equal(stamp.freeze.version_ref, "OVR-CKO-REFERENCE-STANDARDS-UNIVERSE-v1.1.1-20260829");
    assert.equal(stamp.drive.file_id, "1PCPgLrdg5N_ZlBo6kEh0NjR1ydfUzwRn");
    assert.equal(stamp.successor.declared_vs_drive_sha256, "MISMATCH_HOLD");
    assert.equal(stamp.successor.licensed_fulltext, "HOLD_RIGHTS_UNLESS_LICENSED");
    assert.equal(freeze.reference_universe.version_ref, "OVR-CKO-REFERENCE-STANDARDS-UNIVERSE-v1.1.1-20260829");
    assert.equal(freeze.reference_universe.references, 113);
    assert.equal(layers.reference_universe_successor.freeze_replaced, false);
    assert.equal(layers.reference_universe_successor.md_reg_complete, false);
    assert.equal(gateLayers.reference_universe_successor.drive_id, "1PCPgLrdg5N_ZlBo6kEh0NjR1ydfUzwRn");
    assert.equal(catalog.itemCount, catalog.items.length);
    assert.equal(catalog.deployedCount, catalog.items.filter((i) => i.deployed === true).length);
    assert.ok(catalog.items.some((i) => i.id === "1PCPgLrdg5N_ZlBo6kEh0NjR1ydfUzwRn"));
    assert.ok(catalog.items.some((i) => i.id === "1-DCkD2_Lmxe5XTxgLTUc2GgU6qML-5Oe"));
    assert.equal(extractionPolicy.streams.find((s) => s.stream_id === "EXT-REG-CORPUS").count, 0);
    const html = readFileSync(join(site, "cko-estado.html"), "utf8");
    assert.match(html, /v1\.2\.1/);
    assert.match(html, /v1\.1\.1/);
    assert.match(html, /139/);
    assert.equal(html.includes("md_reg_complete: true"), false);
  });
});

describe("MD field universe P01 Drive HOLD", () => {
  it("catalogs P01 reconciliation without claiming classified 2496/10913 materialized", () => {
    const stamp = JSON.parse(readFileSync(join(gatePub, "drive/CKO-RUN-FIELD-UNIVERSE-RECONCILIATION-P01-HOLD.json"), "utf8"));
    const catalog = JSON.parse(readFileSync(join(gatePub, "drive/catalog.json"), "utf8"));
    const gateLayers = JSON.parse(readFileSync(join(gatePub, "data/layers.json"), "utf8"));
    assert.equal(stamp.release_allowed, false);
    assert.equal(stamp.md_reg_complete, false);
    assert.equal(stamp.bindings_materialized, false);
    assert.equal(stamp.run.decision, "PASS_WITH_FINDINGS");
    assert.equal(stamp.run.governed_field_catalog, 1200);
    assert.equal(stamp.run.normative_bindings, 6111);
    assert.equal(stamp.classified.fields_classified, 2496);
    assert.equal(stamp.classified.bindings_classified, 10913);
    assert.equal(stamp.drive.file_id, "1kcYqtqHAGNfmM507TQ0QSQL7d4-V5ekK");
    assert.equal(stamp.run.h08_hold, 48);
    assert.equal(layers.field_universe_reconciliation.bindings_materialized, false);
    assert.equal(layers.field_universe_reconciliation.md_reg_complete, false);
    assert.equal(gateLayers.field_universe_reconciliation.drive_id, "1kcYqtqHAGNfmM507TQ0QSQL7d4-V5ekK");
    assert.equal(catalog.itemCount, catalog.items.length);
    assert.equal(catalog.deployedCount, catalog.items.filter((i) => i.deployed === true).length);
    assert.ok(catalog.items.some((i) => i.id === "1kcYqtqHAGNfmM507TQ0QSQL7d4-V5ekK"));
    assert.equal(extractionPolicy.streams.find((s) => s.stream_id === "EXT-MD-FIELDS").count, 2496);
    assert.equal(layers.master_data_to_frontend.materialized_field_bindings, false);
    const html = readFileSync(join(site, "cko-estado.html"), "utf8");
    assert.match(html, /P01/);
    assert.match(html, /1200/);
    assert.match(html, /6111/);
    assert.match(html, /2496/);
    assert.equal(html.includes("md_reg_complete: true"), false);
    assert.equal(html.includes("bindings_materialized: true"), false);
  });
});

describe("CONTENT-OF-TRUTH backup recovery HOLD", () => {
  it("catalogs the 2026-09-04 reconstruction without claiming bit-identical restore or replacing HORIZONTAL", () => {
    const stamp = JSON.parse(readFileSync(join(gatePub, "drive/CKO-CONTENT-OF-TRUTH-BACKUP-20260903-HOLD.json"), "utf8"));
    const catalog = JSON.parse(readFileSync(join(gatePub, "drive/catalog.json"), "utf8"));
    const gateLayers = JSON.parse(readFileSync(join(gatePub, "data/layers.json"), "utf8"));
    assert.equal(stamp.release_allowed, false);
    assert.equal(stamp.md_reg_complete, false);
    assert.equal(stamp.bit_identical_restore, false);
    assert.equal(stamp.canonical_horizontal_replaced, false);
    assert.equal(stamp.drive.folder_id, "1TZfs0xilYoHMP34nqnnIk8DXdwiEIESd");
    assert.equal(stamp.layers["02_FINAL_CONTROL_WRAPPERS"].wrappers_n, 44);
    assert.equal(stamp.layers["04_RUNTIME_EVIDENCE"].zip_over_9mb_added, 0);
    assert.equal(layers.content_of_truth_backup.bit_identical_restore, false);
    assert.equal(gateLayers.content_of_truth_backup.wrappers_n, 44);
    assert.equal(catalog.itemCount, catalog.items.length);
    assert.equal(catalog.deployedCount, catalog.items.filter((i) => i.deployed === true).length);
    assert.ok(catalog.items.some((i) => i.id === "1TZfs0xilYoHMP34nqnnIk8DXdwiEIESd"));
    assert.ok(catalog.items.some((i) => i.id === "1brLvOSQ7ygwlSZaZeFz4ozBNF-3sl4kXnrNu2pEaRmU"));
    const md = gateLayers.layers.find((l) => l.id === "CKO-MD");
    assert.equal(md.drive_id, "18yyBskfiiKNAduwNmnp8vHO_09Qg_n-0");
    const html = readFileSync(join(site, "cko-estado.html"), "utf8");
    assert.match(html, /CONTENT-OF-TRUTH/);
    assert.match(html, /bit-a-bit|bit-identical|não localizado/i);
    assert.equal(html.includes("md_reg_complete: true"), false);
  });
});

describe("Nurse-PaLM RC v6.5.1 R5 split HOLD", () => {
  it("catalogs the 12-part split without ingesting parts or asserting operational Nurse-PaLM", () => {
    const stamp = JSON.parse(readFileSync(join(gatePub, "drive/CKO-NURSE-PALM-RC-v6_5_1_R5-SPLIT-HOLD.json"), "utf8"));
    const manifest = JSON.parse(readFileSync(join(gatePub, "drive/CKO-NURSE-PALM-RC-v6_5_1_R5-SPLIT_MANIFEST.json"), "utf8"));
    const catalog = JSON.parse(readFileSync(join(gatePub, "drive/catalog.json"), "utf8"));
    const gateLayers = JSON.parse(readFileSync(join(gatePub, "data/layers.json"), "utf8"));
    assert.equal(stamp.release_allowed, false);
    assert.equal(stamp.operational, "NOT_ASSERTED");
    assert.equal(stamp.parts_ingested, false);
    assert.equal(stamp.images_ingested, false);
    assert.equal(stamp.split.parts_n, 12);
    assert.equal(stamp.split.parts_over_9mb, 0);
    assert.equal(stamp.drive.folder_id, "1ogT26MeBxfKC_B2tMsHQuiNTPVvPXZc4");
    assert.equal(manifest.parts.length, 12);
    assert.equal(manifest.member_count, 5692);
    assert.ok(manifest.parts.every((p) => p.bytes < 9000000));
    assert.equal(layers.nurse_palm_split.parts_ingested, false);
    assert.equal(layers.nurse_palm_split.operational, "NOT_ASSERTED");
    assert.equal(gateLayers.nurse_palm_split.folder_id, "1ogT26MeBxfKC_B2tMsHQuiNTPVvPXZc4");
    assert.equal(catalog.nursePalmOperational, "NOT_ASSERTED");
    assert.equal(catalog.itemCount, catalog.items.length);
    assert.equal(catalog.deployedCount, catalog.items.filter((i) => i.deployed === true).length);
    assert.ok(catalog.items.some((i) => i.id === "1ogT26MeBxfKC_B2tMsHQuiNTPVvPXZc4"));
    const html = readFileSync(join(site, "cko-estado.html"), "utf8");
    assert.match(html, /12 partes/);
    assert.match(html, /NOT_ASSERTED/);
    assert.equal(html.includes("operational: true"), false);
    assert.equal(html.includes("parts_ingested: true"), false);
  });
});

describe("Clinical Rules live recovery HOLD", () => {
  it("catalogs seven recovered packs without promoting clinical ACTIVE or replacing HORIZONTAL", () => {
    const stamp = JSON.parse(readFileSync(join(gatePub, "drive/CKO-CLINICAL-RULES-LIVE-RECOVERY-20260904-HOLD.json"), "utf8"));
    const manifest = JSON.parse(readFileSync(join(gatePub, "drive/CKO-CLINICAL-RULES-LIVE-RECOVERY-20260904-MANIFEST.json"), "utf8"));
    const catalog = JSON.parse(readFileSync(join(gatePub, "drive/catalog.json"), "utf8"));
    const gateLayers = JSON.parse(readFileSync(join(gatePub, "data/layers.json"), "utf8"));
    assert.equal(stamp.release_allowed, false);
    assert.equal(stamp.active, false);
    assert.equal(stamp.clinical_promotion, "DENIED");
    assert.equal(stamp.calculators_scales, "PAUSED");
    assert.equal(stamp.canonical_layer_replaced, false);
    assert.equal(stamp.recovery.packs_n, 7);
    assert.equal(stamp.drive.folder_id, "1zu-8feEdPN4P7N5izQaqYml7JkGAm4D2");
    assert.equal(manifest.count, 7);
    assert.equal(manifest.entries.filter((e) => e.source_status === "ACTIVE").length, 2);
    assert.equal(layers.clinical_rules_recovery.clinical_promotion, "DENIED");
    assert.equal(gateLayers.clinical_rules_recovery.packs_n, 7);
    const clin = gateLayers.layers.find((l) => l.id === "LYR-CLIN-RULE-001");
    assert.equal(clin.drive_id, "1gZ_HQ74arWMRNN2yYElnmYzRWZXL76oo");
    assert.equal(catalog.itemCount, catalog.items.length);
    assert.equal(catalog.deployedCount, catalog.items.filter((i) => i.deployed === true).length);
    assert.ok(catalog.items.some((i) => i.id === "1zu-8feEdPN4P7N5izQaqYml7JkGAm4D2"));
    assert.ok(catalog.items.some((i) => i.id === "15xhAeuHqgC2BUJiUJ4gTASz4svxz7rj8"));
    const html = readFileSync(join(site, "cko-estado.html"), "utf8");
    assert.match(html, /7 packs/);
    assert.match(html, /DENIED/);
    assert.equal(html.includes("clinical_promotion: true"), false);
    assert.equal(html.includes("md_reg_complete: true"), false);
  });
});

describe("Clinical calculator lote 002 HTML dump HOLD", () => {
  it("catalogs eight live HTML dumps without ingesting them or unpausing calculators", () => {
    const stamp = JSON.parse(readFileSync(join(gatePub, "drive/CKO-CALC-LOTE-002-HTML-HOLD.json"), "utf8"));
    const catalog = JSON.parse(readFileSync(join(gatePub, "drive/catalog.json"), "utf8"));
    const gateLayers = JSON.parse(readFileSync(join(gatePub, "data/layers.json"), "utf8"));
    assert.equal(stamp.release_allowed, false);
    assert.equal(stamp.html_ingested, false);
    assert.equal(stamp.clinical_promotion, "DENIED");
    assert.equal(stamp.calculators_scales, "PAUSED");
    assert.equal(stamp.dump.files_n, 8);
    assert.equal(stamp.dump.over_9mb, 0);
    assert.equal(stamp.files.length, 8);
    assert.equal(stamp.files.filter((f) => f.lang === "uk-UA").length, 6);
    assert.equal(stamp.files.find((f) => f.name === "heparina.html").already_on_site, false);
    assert.equal(stamp.drive.folder_id, "1UlCrRv653sBgnA5sjc6PpF8TCiNN5nj5");
    assert.equal(existsSync(join(site, "heparina.html")), false);
    assert.equal(layers.calc_lote_002.html_ingested, false);
    assert.equal(gateLayers.calc_lote_002.files_n, 8);
    const calc = gateLayers.layers.find((l) => l.id === "LYR-CLIN-CALC-001");
    assert.equal(calc.drive_id, "1Oxb_DGzeNlS070s-_f4nuFGAchaXGHAg");
    assert.equal(catalog.itemCount, catalog.items.length);
    assert.equal(catalog.deployedCount, catalog.items.filter((i) => i.deployed === true).length);
    assert.ok(catalog.items.some((i) => i.id === "1UlCrRv653sBgnA5sjc6PpF8TCiNN5nj5"));
    const html = readFileSync(join(site, "cko-estado.html"), "utf8");
    assert.match(html, /lote 002/i);
    assert.match(html, /8 HTML/);
    assert.match(html, /html_ingested: false/);
    assert.equal(html.includes("html_ingested: true"), false);
    assert.equal(html.includes("md_reg_complete: true"), false);
  });
});

