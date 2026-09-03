#!/usr/bin/env node
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { runGates } from "./public/engine/core.js";

const root = dirname(fileURLToPath(import.meta.url));
const universe = JSON.parse(readFileSync(join(root, "public/data/universe.json"), "utf8"));
const report = await runGates(universe, { action: "inspect" });

const outDir = join(root, "public/data");
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
}, null, 2));
