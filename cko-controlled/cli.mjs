#!/usr/bin/env node
import { readFileSync, writeFileSync, mkdirSync, readdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { CASCADE, runGates, RUNTIME_PAGES } from "./public/engine/core.js";

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
const pendenciesPath = join(gatePub, "data/pendencies.json");
const pendencies = existsSync(pendenciesPath) ? JSON.parse(readFileSync(pendenciesPath, "utf8")) : undefined;
const driveImmutablePath = join(gatePub, "data/drive-immutable.json");
const driveImmutable = existsSync(driveImmutablePath) ? JSON.parse(readFileSync(driveImmutablePath, "utf8")) : undefined;
const platform = { listing, files, toolLibrary, governance, pendencies, driveImmutable };

const report = await runGates(universe, { action: "inspect", platform });

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
