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
  CASCADE,
  RUNTIME_PAGES,
  TOOL_RUNTIME_CANARIES,
  LIBRARY_RUNTIME_CANARIES,
  TOOL_ENGINE_LIBS,
} from "../public/engine/core.js";

const root = dirname(fileURLToPath(import.meta.url));
const gatePub = join(root, "../public");
const site = join(root, "../../reference-website");
const universe = JSON.parse(readFileSync(join(gatePub, "data/universe.json"), "utf8"));
const toolLibrary = JSON.parse(readFileSync(join(site, "data/cko/tool-library-runtime.json"), "utf8"));
const governance = JSON.parse(readFileSync(join(site, "data/cko/governance.json"), "utf8"));
const pendencies = JSON.parse(readFileSync(join(gatePub, "data/pendencies.json"), "utf8"));
const driveImmutable = JSON.parse(readFileSync(join(gatePub, "data/drive-immutable.json"), "utf8"));
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
  pendencies,
  driveImmutable,
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
    assert.ok(policy.rules.some((r) => r.id === "PENDENCIES_EXPLICIT"));
    assert.ok(policy.rules.some((r) => r.id === "DRIVE_IMMUTABLE"));
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
  });
});

describe("software verification", () => {
  it("property-based: mutations cannot sneak a release", () => {
    const r = propertyBased(universe);
    assert.equal(r.ok, true, JSON.stringify(r.trials.filter((t) => !t.blocked)));
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
  });
});

describe("CI gates", () => {
  it("passes the defined gate set without releasing", async () => {
    const r = await runGates(universe, { platform });
    assert.equal(r.ok, true, JSON.stringify(r.failed));
    assert.equal(r.release, "HOLD / NOT_RELEASED");
    assert.equal(r.starts_at, "policy-as-code");
    assert.deepEqual(r.cascade.map((g) => g.id), CASCADE);
    assert.ok(r.gates.every((g) => g.ok && g.status === "PASS"));
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
    const byId = Object.fromEntries(pendencies.items.map((i) => [i.id, i]));
    assert.equal(byId["PEND-DIR-ASA-TOOL-CONFIG"].status, "CREATED_IN_RUNTIME_HOLD");
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
});
