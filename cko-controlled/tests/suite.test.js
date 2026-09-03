import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  validateSchema,
  validateRuntimePlatformSchema,
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
} from "../public/engine/core.js";

const root = dirname(fileURLToPath(import.meta.url));
const pub = join(root, "../public");
const universe = JSON.parse(readFileSync(join(pub, "data/universe.json"), "utf8"));
const platform = {
  listing: readdirSync(pub),
  files: Object.fromEntries(RUNTIME_PAGES.map((p) => [p, readFileSync(join(pub, p), "utf8")])),
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
    const policy = JSON.parse(readFileSync(join(pub, "policies/fail-closed.json"), "utf8"));
    const schema = JSON.parse(readFileSync(join(pub, "schemas/runtime-platform.schema.json"), "utf8"));
    assert.equal(policy.root, true);
    assert.equal(policy.kind, "policy-as-code");
    assert.deepEqual(policy.cascade, CASCADE);
    assert.deepEqual(schema.properties.pages.items.enum, RUNTIME_PAGES);
    assert.ok(policy.rules.some((r) => r.id === "NO_REPORT_DASHBOARD"));
    assert.ok(policy.rules.some((r) => r.id === "RUNTIME_IS_DRIVE_PLATFORM"));
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
