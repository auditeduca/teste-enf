#!/usr/bin/env node
import { readFileSync, writeFileSync, mkdirSync, readdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { CASCADE, runGates, RUNTIME_PAGES } from "./public/engine/core.js";

const root = dirname(fileURLToPath(import.meta.url));
const pub = join(root, "public");
const policy = JSON.parse(readFileSync(join(pub, "policies/fail-closed.json"), "utf8"));
if (!policy.root || policy.kind !== "policy-as-code" || JSON.stringify(policy.cascade) !== JSON.stringify(CASCADE)) {
  console.error("CKO GATE FAIL policy-as-code root mismatch");
  process.exit(1);
}
const universe = JSON.parse(readFileSync(join(pub, "data/universe.json"), "utf8"));
const listing = readdirSync(pub);
const files = Object.fromEntries(
  [...RUNTIME_PAGES, "aldrete.html"].filter((p) => existsSync(join(pub, p))).map((p) => [p, readFileSync(join(pub, p), "utf8")])
);
const toolLibraryPath = join(pub, "data/tool-library-runtime.json");
const toolLibrary = existsSync(toolLibraryPath) ? JSON.parse(readFileSync(toolLibraryPath, "utf8")) : undefined;
const pendenciesPath = join(pub, "data/pendencies.json");
const pendencies = existsSync(pendenciesPath) ? JSON.parse(readFileSync(pendenciesPath, "utf8")) : undefined;
const driveImmutablePath = join(pub, "data/drive-immutable.json");
const driveImmutable = existsSync(driveImmutablePath) ? JSON.parse(readFileSync(driveImmutablePath, "utf8")) : undefined;
const platform = { listing, files, toolLibrary, pendencies, driveImmutable };

const report = await runGates(universe, { action: "inspect", platform });

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
