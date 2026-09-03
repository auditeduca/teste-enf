import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  validateSchema,
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
} from "../public/engine/core.js";

const root = dirname(fileURLToPath(import.meta.url));
const universe = JSON.parse(readFileSync(join(root, "../public/data/universe.json"), "utf8"));

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
});

describe("policy-as-code", () => {
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
    const r = await runGates(universe);
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
    const pub = join(root, "../public");
    const index = readFileSync(join(pub, "index.html"), "utf8");
    assert.match(index, /Calculadoras de Enfermagem/);
    assert.equal(index.includes('id="graph"'), false);
    assert.equal(index.includes("Reexecutar cascata"), false);
    assert.equal(index.includes("orquestrador"), false);
    const pages = [
      "missao.html",
      "objetivo.html",
      "ecossistema.html",
      "acessibilidade.html",
      "tecnologiaverde.html",
      "privacidade.html",
      "politica-editorial.html",
      "notificacoes-legais.html",
      "fale.html",
      "forum-enfermagem.html",
      "mapa-do-site.html",
    ];
    for (const p of pages) {
      const html = readFileSync(join(pub, p), "utf8");
      assert.ok(html.includes("<main"), p);
      assert.equal(html.includes('canvas id="graph"'), false, p);
    }
    assert.equal(readdirSync(pub).includes("app.js"), false);
  });
});
