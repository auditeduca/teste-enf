import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { execSync } from "node:child_process";
import { mkdtempSync, readFileSync, readdirSync, existsSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
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
  MD_REG_CHAIN,
  MD_REG_POLICY_ID,
  UT_POLICY_ID,
  UT_DOCUMENT_ID,
  UT_CONTROL_N,
  UT_MD_GATE,
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
  it("keeps Aldrete/IMC with static hero so the shell must skip the slot", () => {
    for (const name of ["aldrete.html", "imc.html"]) {
      const html = readFileSync(join(site, name), "utf8");
      assert.match(html, /data-cko-slot="hero"/);
      assert.match(html, /<h1\b/);
    }
    const missao = readFileSync(join(site, "missao.html"), "utf8");
    assert.match(missao, /class="crumbs"/);
    assert.match(missao, /<section class="hero"/);
    assert.equal(missao.includes("data-cko-slot="), false);
  });
});

describe("GitHub Pages CALENF runtime", () => {
  it("stages reference-website with project-site base and site-pattern canaries", () => {
    const out = mkdtempSync(join(tmpdir(), "cko-pages-"));
    try {
      execSync(`python3 scripts/prepare_github_pages.py --out ${out} --base /teste-enf`, {
        cwd: join(root, ".."),
        encoding: "utf8",
      });
      const index = readFileSync(join(out, "index.html"), "utf8");
      assert.match(index, /PAGE_INSTITUTIONAL_CLUSTER/);
      assert.match(index, /<base href="\/teste-enf\/">/);
      assert.match(index, /href="\/teste-enf\/public\/output\.css"/);
      assert.equal(existsSync(join(out, "aldrete.html")), true);
      assert.equal(existsSync(join(out, "camadas", "index.html")), true);
      assert.equal(existsSync(join(out, ".nojekyll")), true);
      assert.equal(existsSync(join(out, "admin.html")), false);
      assert.equal(existsSync(join(out, "zh")), false);
      const mapa = readFileSync(join(site, "mapa-do-site.html"), "utf8");
      assert.match(mapa, /href="\/camadas\/"/);
      assert.match(mapa, /href="\/aldrete\.html"/);
      assert.match(mapa, /href="\/cko-hold-preview\.html"/);
      assert.equal(existsSync(join(out, "cko-hold-preview.html")), true);
    } finally {
      rmSync(out, { recursive: true, force: true });
    }
  });
});

describe("HOLD localStorage preview", () => {
  it("ships a single-file CALENF preview seeded into CKO_HOLD_PREVIEW_V1", () => {
    const html = readFileSync(join(site, "cko-hold-preview.html"), "utf8");
    const snap = JSON.parse(readFileSync(join(site, "data/cko/hold-preview.json"), "utf8"));
    assert.match(html, /CKO_HOLD_PREVIEW_V1/);
    assert.match(html, /Calculadoras de Enfermagem/);
    assert.match(html, /localStorage/);
    assert.match(html, /Não autoriza deploy|Não é deploy/);
    assert.equal(snap.id, "CKO-HOLD-PREVIEW-1.0.0");
    assert.equal(snap.layer_count, 44);
    assert.equal(snap.layers.length, 44);
    assert.equal(snap.release_allowed, false);
    assert.equal(snap.deploy, false);
    assert.equal(snap.home.title, "Calculadoras de Enfermagem");
    assert.ok(snap.tools.some((t) => t.id === "aldrete"));
    assert.ok(snap.tools.some((t) => t.id === "imc"));
    assert.ok((snap.specialties || []).length >= 12);
    assert.ok(snap.pages.some((p) => p.id === "mapa"));
  });
});
