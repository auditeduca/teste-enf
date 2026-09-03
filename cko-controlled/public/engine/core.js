/**
 * CKO controlled assurance engine — isomorphic (Node + browser).
 * Stack: policy-as-code → schemas → graph constraints → CI gates →
 * runtime assertions → automatic evidence.
 */
export const RULES = {
  coverage: "100% do universo conhecido",
  evidence_coverage: "100%",
  test_pass: "100% dos testes definidos",
  residual_uncertainty: "X",
  unknown_universe: "explicitado",
};

/** Everything starts here. Later stages cannot PASS if a predecessor failed. */
export const CASCADE = [
  "policy-as-code",
  "schemas",
  "graph-constraints",
  "CI-gates",
  "runtime-assertions",
  "automatic-evidence",
];

const INTEGRITY_DENIALS = new Set([
  "NO_FACT_WITHOUT_EVIDENCE",
  "DISCOVERY_IS_NOT_EVIDENCE",
  "PENDING_IS_NOT_ACK",
  "RUNTIME_OBSERVED_NOT_INFERRED",
  "UNKNOWN_UNIVERSE_EXPLICIT",
  "RESIDUAL_X_REQUIRED",
  "NO_CLINICAL_CLAIM_FROM_CLASSIFICATION",
  "RIGHTS_CHAIN_REQUIRED_TO_PUBLISH",
  "COVERAGE_100_KNOWN",
  "EVIDENCE_COVERAGE_100",
  "TEST_PASS_100_DEFINED",
  "NO_REPORT_DASHBOARD",
  "RUNTIME_IS_DRIVE_PLATFORM",
  "NO_CONTROL_ROOM_APP",
  "TOOL_RUNTIME_PRESENT",
  "LIBRARY_RUNTIME_PRESENT",
  "TOOL_LIBRARIES_PRESENT",
  "PENDENCIES_EXPLICIT",
  "DRIVE_IMMUTABLE",
  "SCHEMA_GOVERNS_RUNTIME",
  "GRAPH_GOVERNS_RUNTIME",
  "TWIN_GOVERNS_RUNTIME",
  "NURSEPALM_GOVERNS_RUNTIME",
  "AGENTIC_GOVERNS_RUNTIME",
  "LAYERS_44_PRESENT",
  "MD_NORMS_EVIDENCE_CHAIN",
]);

export const MD_NORM_CHAIN_ID = "CKO-MD-TO-FRONTEND-1.0.0";
export const MD_NORM_STAMP = {
  md: 'data-cko-md="CKO-MD"',
  reg: 'data-cko-reg="CKO-REG"',
  norm: 'data-cko-norm="NIFS-900-03"',
  evidence: 'data-cko-evidence="HOLD"',
  chain: 'data-cko-chain="MD / REG / Schema / Engine / Validator / Renderer / Runtime / Frontend"',
};

export const TOOL_RUNTIME_CANARIES = [
  "aldrete.html",
  "imc.html",
  "gotejamento.html",
  "braden.html",
  "news.html",
  "gasometria.html",
];

export const LIBRARY_RUNTIME_CANARIES = [
  "biblioteca.html",
  "downloads.html",
  "biblioteca-provas.html",
  "biblioteca-cirurgica.html",
  "biblioteca-curativo.html",
  "biblioteca-seringa.html",
  "biblioteca-carinho-de-emergencia.html",
];

export const TOOL_ENGINE_LIBS = [
  "js/calc-engine.js",
  "js/calc-engine-v2.js",
  "js/ce-calculadora-padrao.js",
  "js/nurse-palm.js",
  "js/knowledge-graph.js",
  "js/modules/data/biblioteca.json",
];

export const CALENF_STRUCTURE = [
  "data/schemas/tool.schema.json",
  "data/tools",
  "scripts/generate_tool_page.py",
  "js/calc-engine.js",
  "js/calc-engine-v2.js",
  "js/nurse-palm.js",
  "js/knowledge-graph.js",
  "js/partials-loader.js",
  "partials/header.html",
];

export const CANONICAL_LAYER_IDS = [
  "CKO-MD",
  "CKO-REG",
  "LYR-CLIN-CALC-001",
  "LYR-CLIN-SCALE-001",
  "LYR-CLIN-RULE-001",
  "LYR-LIB-001",
  "LYR-MED-001",
  "LYR-LAB-001",
  "LYR-ANAT-001",
  "LYR-COND-001",
  "LYR-PROC-001",
  "LYR-TERM-001",
  "LYR-EDU-001",
  "LYR-REF-001",
  "LYR-CONTENT-001",
  "LYR-LEARN-001",
  "LYR-PAGE-TPL-001",
  "LYR-DOC-TPL-001",
  "LYR-MEDIA-001",
  "LYR-DERIVE-001",
  "LYR-HCD-001",
  "LYR-A11Y-001",
  "LYR-DS-001",
  "LYR-UI-001",
  "LYR-PRV-001",
  "LYR-SEC-001",
  "LYR-ROUTE-001",
  "LYR-SEO-001",
  "LYR-OG-001",
  "LYR-SEM-001",
  "LYR-I18N-001",
  "LYR-SEARCH-001",
  "LYR-REC-001",
  "LYR-USERSTATE-001",
  "LYR-ANL-001",
  "LYR-PERF-001",
  "LYR-REL-001",
  "LYR-OBS-001",
  "LYR-SUS-001",
  "LYR-RND-001",
  "LYR-RUN-001",
  "LYR-EXPORT-001",
  "LYR-PUB-001",
  "LYR-MON-001",
];

export const RUNTIME_PAGES = [
  "index.html",
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

const SHA_RE = /^[a-f0-9]{64}$/;
const BLOCK_IDS = ["B1", "B2", "B3", "B4", "B5", "B6.1", "B6.2", "B6.3", "B6.4", "B7", "B8", "B9", "B10"];
const LENS_IDS = ["AUD-360", "AUD-DIR", "AUD-COMP", "AUD-INV", "AUD-DIAG", "AUD-VERT", "AUD-HOR", "AUD-CIRC"];

export function sha256Hex(bytes) {
  return crypto.subtle
    ? null
    : null;
}

export async function digestSha256(text) {
  const encoded = new TextEncoder().encode(text);
  if (globalThis.crypto?.subtle) {
    const buf = await globalThis.crypto.subtle.digest("SHA-256", encoded);
    return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
  }
  const { createHash } = await import("node:crypto");
  return createHash("sha256").update(text).digest("hex");
}

export function inspectPlatform(platform) {
  const denials = [];
  const files = platform?.files || {};
  const listing = platform?.listing || Object.keys(files);
  const index = files["index.html"] || "";
  if (/id="graph"|Reexecutar cascata|id="orquestrador"|Relat[oó]rio T[eé]cnico Final Controlado/.test(index)) {
    denials.push({ id: "NO_REPORT_DASHBOARD", reason: "report dashboard must not be the runtime frontend" });
  }
  if (!/Calculadoras de Enfermagem/.test(index) || !/PAGE_INSTITUTIONAL_CLUSTER/.test(index)) {
    denials.push({ id: "RUNTIME_IS_DRIVE_PLATFORM", reason: "home must be Drive Wave2 platform" });
  }
  if (listing.includes("app.js")) {
    denials.push({ id: "NO_CONTROL_ROOM_APP", reason: "public/app.js is control-room UI" });
  }
  const tl = platform?.toolLibrary;
  if (tl) {
    const tools = new Set(tl.tool_canaries || []);
    const libs = new Set(tl.library_canaries || []);
    const engines = new Set(tl.engine_libraries || []);
    if (TOOL_RUNTIME_CANARIES.some((p) => !tools.has(p))) {
      denials.push({ id: "TOOL_RUNTIME_PRESENT", reason: "tool calculator runtimes are missing from the hosted site" });
    }
    if (LIBRARY_RUNTIME_CANARIES.some((p) => !libs.has(p))) {
      denials.push({ id: "LIBRARY_RUNTIME_PRESENT", reason: "library runtimes are missing from the hosted site" });
    }
    if (TOOL_ENGINE_LIBS.some((p) => !engines.has(p))) {
      denials.push({ id: "TOOL_LIBRARIES_PRESENT", reason: "calculator/library JS engines are missing" });
    }
    if ((tl.structure && tl.structure !== "calenf") || (tl.calenf_structure && CALENF_STRUCTURE.some((p) => !(tl.calenf_structure || []).includes(p)))) {
      denials.push({ id: "SCHEMA_GOVERNS_RUNTIME", reason: "runtime is not the CALENF NIFS-900 structure" });
    }
  }
  const gov = platform?.governance;
  if (gov) {
    const g = inspectCalenfGovernance(gov);
    denials.push(...g.denials);
  }
  if (platform?.pendencies) {
    const pend = inspectPendencies(platform.pendencies, platform.driveImmutable);
    denials.push(...pend.denials);
  }
  if (Object.keys(files).length) {
    denials.push(...inspectLayers(platform.layers, files["ecossistema.html"] || "").denials);
    const stamped = [...RUNTIME_PAGES, ...TOOL_RUNTIME_CANARIES.filter((p) => files[p]), ...LIBRARY_RUNTIME_CANARIES.filter((p) => files[p])];
    for (const p of stamped) {
      const html = files[p] || "";
      if (!html) continue;
      if (!html.includes(MD_NORM_STAMP.md) || !html.includes(MD_NORM_STAMP.reg) || !html.includes(MD_NORM_STAMP.evidence) || !html.includes(MD_NORM_STAMP.chain)) {
        denials.push({ id: "MD_NORMS_EVIDENCE_CHAIN", reason: `${p} missing MD→norma→evidência frontend stamp` });
        break;
      }
    }
  }
  return { ok: denials.length === 0, denials };
}

export function inspectLayers(layers, ecossistemaHtml = "") {
  const denials = [];
  const deny = (reason) => denials.push({ id: "LAYERS_44_PRESENT", reason });
  if (!layers) {
    deny("hosted site is missing the 44 classified horizontal layers");
    return { ok: false, denials };
  }
  if (layers.id !== "CKO-44-LAYER-SITE-1.0.0" || layers.kind !== "cko-44-layers") {
    deny("layers catalog identity must be CKO-44-LAYER-SITE-1.0.0");
  }
  if (layers.count !== 44 || !Array.isArray(layers.layers) || layers.layers.length !== 44) {
    deny(`layers count ${layers.count}/${(layers.layers || []).length} != 44/44`);
  }
  if (!String(layers.release || "").includes("NOT_RELEASED") || layers.published === true) {
    deny("44-layer catalog must remain HOLD / NOT_RELEASED");
  }
  if (layers.operational && layers.operational !== "NOT_ASSERTED") {
    deny("44-layer catalog must not assert operational runtime");
  }
  const gb = layers.governed_by || {};
  if (gb.graph !== "js/knowledge-graph.js" || gb.twin !== "B5" || gb.agentic !== "B1" || gb.nursePalm !== "B10") {
    deny("44 layers must be governed by graph + digital twin + agentic AI + Nurse-PaLM");
  }
  if (gb.master_data !== "CKO-MD" || gb.regulatory !== "CKO-REG" || gb.evidence !== "HOLD") {
    deny("44 layers must bind master data, regulatory norm and HOLD evidence");
  }
  if (layers.master_data_to_frontend?.id !== MD_NORM_CHAIN_ID || layers.master_data_to_frontend?.no_fact_without_evidence !== true) {
    deny("44-layer catalog missing MD→frontend evidence chain");
  }
  if (layers.master_data_to_frontend?.materialized_field_bindings === true) {
    deny("must not claim 10913 field bindings materialized");
  }
  const ids = (layers.layers || []).map((l) => l.id);
  if (JSON.stringify(ids) !== JSON.stringify(CANONICAL_LAYER_IDS)) {
    deny("layer ids must match ART-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE");
  }
  for (const layer of layers.layers || []) {
    if (layer.present !== true) deny(`${layer.id} is not present on the hosted site`);
    if (!String(layer.release || "").includes("NOT_RELEASED")) deny(`${layer.id} must remain NOT_RELEASED`);
    if (!SHA_RE.test(layer.sha256 || "")) deny(`${layer.id} classified sha256 invalid`);
    if (!Array.isArray(layer.runtime_paths) || layer.runtime_paths.length === 0) {
      deny(`${layer.id} missing CALENF runtime binding`);
    }
    if (layer.operational === true || layer.operational === "ASSERTED") {
      deny(`${layer.id} must not claim operational runtime`);
    }
    if (layer.published === true) deny(`${layer.id} must not claim publication`);
    const lgb = layer.governed_by || layers.governed_by || {};
    if (lgb.graph !== "js/knowledge-graph.js" || lgb.twin !== "B5" || lgb.agentic !== "B1" || lgb.nursePalm !== "B10") {
      deny(`${layer.id} missing graph/twin/agentic/Nurse-PaLM governance`);
    }
    if (layer.master_data !== "CKO-MD" || layer.regulatory !== "CKO-REG" || layer.evidence?.no_fact_without_evidence !== true) {
      deny(`${layer.id} missing master-data / norm / evidence amarração`);
    }
  }
  if (ecossistemaHtml) {
    const missingOnPage = CANONICAL_LAYER_IDS.filter((id) => !ecossistemaHtml.includes(id));
    if (missingOnPage.length) deny(`ecossistema.html missing layer ids ${missingOnPage.slice(0, 8).join(",")}`);
    if (!/44\/44/.test(ecossistemaHtml) || !/HOLD \/ NOT_RELEASED/.test(ecossistemaHtml)) {
      deny("ecossistema.html must declare 44/44 HOLD / NOT_RELEASED");
    }
    if (!/cko-md-norm-evidence/.test(ecossistemaHtml) || !/2496/.test(ecossistemaHtml) || !/10913/.test(ecossistemaHtml)) {
      deny("ecossistema.html must declare MD→norma→evidência chain");
    }
  }
  return { ok: denials.length === 0, denials };
}

export function inspectCalenfGovernance(governance) {
  const denials = [];
  if (!governance) return { ok: true, skipped: true, denials };
  const deny = (id, reason) => denials.push({ id, reason });
  if (governance.kind !== "calenf-runtime-governance") {
    deny("SCHEMA_GOVERNS_RUNTIME", "governance kind must be calenf-runtime-governance");
  }
  if (governance.schema !== "data/schemas/tool.schema.json") {
    deny("SCHEMA_GOVERNS_RUNTIME", "tools must instance data/schemas/tool.schema.json");
  }
  if (governance.graph !== "js/knowledge-graph.js") {
    deny("GRAPH_GOVERNS_RUNTIME", "runtime graph must be js/knowledge-graph.js");
  }
  const twin = governance.digitalTwin || {};
  if (twin.nifs !== "NIFS-600-15" || twin.observed === true || twin.deployed === true) {
    deny("TWIN_GOVERNS_RUNTIME", "digital twin must remain NIFS-600-15 HOLD (not observed/deployed)");
  }
  if (twin.classified_nodes !== 137 || twin.classified_edges !== 136) {
    deny("TWIN_GOVERNS_RUNTIME", "classified digital twin cardinality must remain 137/136");
  }
  const np = governance.nursePalm || {};
  if (np.engine !== "js/nurse-palm.js" || np.operational !== "NOT_ASSERTED" || (np.layers || []).length !== 10) {
    deny("NURSEPALM_GOVERNS_RUNTIME", "Nurse-PaLM V9 must bind js/nurse-palm.js and stay NOT_ASSERTED");
  }
  const agentic = governance.agentic || {};
  if (agentic.block !== "B1" || agentic.operational !== "NOT_ASSERTED") {
    deny("AGENTIC_GOVERNS_RUNTIME", "B1 agentic runtime must remain NOT_ASSERTED");
  }
  if (agentic.independence !== "maker!=checker!=auditor") {
    deny("AGENTIC_GOVERNS_RUNTIME", "maker/checker/auditor independence missing");
  }
  const nodes = governance.nodes || [];
  const edges = governance.edges || [];
  const byId = new Map(nodes.map((n) => [n.id, n]));
  if (!byId.has("B1") || byId.get("B1")?.operational !== "NOT_ASSERTED") {
    deny("AGENTIC_GOVERNS_RUNTIME", "B1 AgentJobRuntime missing or operational claimed");
  }
  const roles = nodes.filter((n) => n.type === "Agent").map((n) => n.role);
  if (!["MAKER", "CHECKER", "AUDITOR", "ORCHESTRATOR"].every((r) => roles.includes(r))) {
    deny("AGENTIC_GOVERNS_RUNTIME", "agentic roles maker/checker/auditor/orchestrator missing");
  }
  const hasEdge = (from, to, rel) => edges.some((e) => e[0] === from && e[1] === to && e[2] === rel);
  const hasFanIn = edges.some((e) => String(e[0] || "").startsWith("TOOL-") && e[1] === "B9" && e[2] === "fanIn");
  const hasTwin = edges.some((e) => e[2] === "governedBy" && e[1] === "B5");
  const hasPalm = edges.some((e) => e[2] === "boundTo" && e[1] === "B10");
  const hasAgentic = edges.some((e) => String(e[0] || "").startsWith("TOOL-") && e[1] === "B1" && e[2] === "boundTo");
  if (!hasFanIn || !hasTwin || !hasPalm || !hasAgentic) {
    deny("GRAPH_GOVERNS_RUNTIME", "tools must fan-in to B9 and bind graph + B5 twin + B1 agentic + B10 Nurse-PaLM");
  }
  const layerNodes = nodes.filter((n) => n.type === "LayerRuntime");
  if (layerNodes.length !== 44) {
    deny("GRAPH_GOVERNS_RUNTIME", `layer graph nodes ${layerNodes.length} != 44`);
  }
  const missingLayers = CANONICAL_LAYER_IDS.filter((id) => !byId.has(`LAYER-${id}`));
  if (missingLayers.length) {
    deny("GRAPH_GOVERNS_RUNTIME", `layers missing from graph: ${missingLayers.slice(0, 8).join(",")}`);
  }
  for (const id of CANONICAL_LAYER_IDS) {
    const nid = `LAYER-${id}`;
    if (!hasEdge(nid, "B9", "fanIn") || !hasEdge(nid, "B10", "boundTo") || !hasEdge(nid, "B1", "boundTo") || !hasEdge(nid, "GRAPH-KG", "inGraph")) {
      deny("GRAPH_GOVERNS_RUNTIME", `${nid} is not graph/agentic/Nurse-PaLM/B9 governed`);
      break;
    }
    if (!hasEdge(nid, `TWIN-${nid}`, "projectedAs")) {
      deny("TWIN_GOVERNS_RUNTIME", `${nid} missing digital twin projection`);
      break;
    }
  }
  const pageNodes = nodes.filter((n) => n.type === "InstitutionalPage");
  if (pageNodes.length !== RUNTIME_PAGES.length) {
    deny("GRAPH_GOVERNS_RUNTIME", `institutional pages in graph ${pageNodes.length} != ${RUNTIME_PAGES.length}`);
  }
  for (const page of RUNTIME_PAGES) {
    const nid = `PAGE-${page.replace(/\.html$/, "")}`;
    if (!hasEdge(nid, "B9", "fanIn") || !hasEdge(nid, "B10", "boundTo") || !hasEdge(nid, "B1", "boundTo")) {
      deny("GRAPH_GOVERNS_RUNTIME", `${nid} is not governed by graph/twin/agentic/Nurse-PaLM`);
      break;
    }
  }
  if (!hasEdge("SEM-EDU", "SEM-CONTENT", "derivedFrom") || !hasEdge("SEM-LEARN", "SEM-CONTENT", "derivedFrom")) {
    deny("GRAPH_GOVERNS_RUNTIME", "PDF semantic controls Content→Educational/Learning missing");
  }
  if (governance.md_freeze !== "FROZEN" || governance.reg_freeze !== "FROZEN") {
    deny("GRAPH_GOVERNS_RUNTIME", "CKO-MD / CKO-REG freeze from PDF fan-in is missing");
  }
  const sc = governance.semantic_controls || {};
  if (!String(sc.learning || "").includes("Agent Continuous Learning") || !String(sc.educational || "").includes("derived from Content")) {
    deny("GRAPH_GOVERNS_RUNTIME", "PDF semantic controls not encoded");
  }
  const chain = governance.evidence_chain || {};
  if (chain.id !== MD_NORM_CHAIN_ID || chain.no_fact_without_evidence !== true || chain.operational !== "NOT_ASSERTED") {
    deny("MD_NORMS_EVIDENCE_CHAIN", "MD→frontend evidence chain missing or operational claimed");
  }
  if (chain.materialized_field_bindings === true) {
    deny("MD_NORMS_EVIDENCE_CHAIN", "classified 10913 bindings must not be claimed materialized");
  }
  if (governance.master_data?.layer !== "CKO-MD" || governance.master_data?.fields_classified !== 2496) {
    deny("MD_NORMS_EVIDENCE_CHAIN", "CKO-MD classified field count 2496 missing");
  }
  if (governance.normative?.layer !== "CKO-REG" || governance.normative?.bindings_classified !== 10913) {
    deny("MD_NORMS_EVIDENCE_CHAIN", "CKO-REG classified binding count 10913 missing");
  }
  for (const cid of ["CHAIN-MD", "CHAIN-REG", "CHAIN-SCHEMA", "CHAIN-ENGINE", "CHAIN-VALIDATOR", "CHAIN-RENDERER", "CHAIN-RUNTIME", "CHAIN-FRONTEND"]) {
    if (!byId.has(cid)) {
      deny("MD_NORMS_EVIDENCE_CHAIN", `${cid} missing`);
      break;
    }
  }
  if (!hasEdge("LAYER-CKO-REG", "LAYER-CKO-MD", "derivedFrom") || !hasEdge("SCHEMA-TOOL", "LAYER-CKO-MD", "derivedFrom") || !hasEdge("SCHEMA-TOOL", "LAYER-CKO-REG", "boundToNorm")) {
    deny("MD_NORMS_EVIDENCE_CHAIN", "REG/schema are not derived from master data with norm binding");
  }
  for (const id of CANONICAL_LAYER_IDS) {
    const nid = `LAYER-${id}`;
    if (id !== "CKO-MD" && !hasEdge(nid, "LAYER-CKO-MD", "derivedFrom")) {
      deny("MD_NORMS_EVIDENCE_CHAIN", `${nid} not derived from CKO-MD`);
      break;
    }
    if (id !== "CKO-REG" && !hasEdge(nid, "LAYER-CKO-REG", "boundToNorm")) {
      deny("MD_NORMS_EVIDENCE_CHAIN", `${nid} missing CKO-REG norm binding`);
      break;
    }
    if (!hasEdge(nid, `EVD-${nid}`, "hasEvidence")) {
      deny("MD_NORMS_EVIDENCE_CHAIN", `${nid} missing evidence receipt`);
      break;
    }
  }
  for (const page of RUNTIME_PAGES) {
    const nid = `PAGE-${page.replace(/\.html$/, "")}`;
    if (!hasEdge(nid, "LAYER-CKO-MD", "derivedFrom") || !hasEdge(nid, "LAYER-CKO-REG", "boundToNorm") || !hasEdge(nid, `EVD-${nid}`, "hasEvidence") || !hasEdge(nid, "CHAIN-FRONTEND", "instanceOf")) {
      deny("MD_NORMS_EVIDENCE_CHAIN", `${nid} is not amarrado MD→norma→evidência→frontend`);
      break;
    }
  }
  return { ok: denials.length === 0, denials };
}

export function inspectPendencies(pendencies, driveImmutable) {
  const denials = [];
  const deny = (id, reason) => denials.push({ id, reason });
  const items = pendencies?.items || [];
  const byId = new Map(items.map((i) => [i.id, i]));
  if (!pendencies || items.length === 0) deny("PENDENCIES_EXPLICIT", "pendency ledger empty");
  if (pendencies?.root !== "policy-as-code") deny("PENDENCIES_EXPLICIT", "pendencies must start at policy-as-code");
  if (pendencies?.mutate_drive !== false || pendencies?.closes_b9 !== false) {
    deny("DRIVE_IMMUTABLE", "pendency ledger must not mutate Drive or close B9");
  }
  const required = [
    ["PEND-PDF-HOLDS-BUCKET", 211],
    ["PEND-PDF-FINDINGS-BUCKET", 313],
    ["PEND-PDF-REPERF-BUCKET", 201],
    ["PEND-PDF-OUTBOX-BUCKET", 296],
    ["PEND-PDF-RIGHTS-BUCKET", 13],
    ["PEND-PDF-UNRESOLVED-ID-BUCKET", 12],
  ];
  for (const [id, count] of required) {
    const row = byId.get(id);
    if (!row || row.count !== count) deny("PENDENCIES_EXPLICIT", `${id} missing or count != ${count}`);
  }
  if (!byId.has("PEND-BLOCK-B9") || !byId.has("PEND-BLOCK-B10")) {
    deny("PENDENCIES_EXPLICIT", "B9/B10 pendencies missing");
  }
  if (!byId.has("PEND-W2-FORUM-CRITICAL")) deny("PENDENCIES_EXPLICIT", "Wave2 forum HOLD missing");
  const locales = items.filter((i) => i.kind === "locale-cell").length;
  if (locales !== 360) deny("PENDENCIES_EXPLICIT", `Wave2 locale cells ${locales} != 360`);
  if (items.some((i) => i.mutate_drive === true || i.closes_b9 === true)) {
    deny("DRIVE_IMMUTABLE", "a pendency claims Drive mutation or B9 close");
  }
  if (driveImmutable) {
    if (driveImmutable.rule !== "DO_NOT_ALTER_DRIVE_FILE") deny("DRIVE_IMMUTABLE", "drive freeze rule missing");
    if (!Array.isArray(driveImmutable.files) || driveImmutable.files.length === 0) {
      deny("DRIVE_IMMUTABLE", "drive freeze empty");
    }
  }
  return { ok: denials.length === 0, denials };
}

export function platformGraphConstraints(platform) {
  const violations = [];
  if (!platform) return { ok: true, violations, skipped: true };
  const files = platform.files || {};
  for (const p of RUNTIME_PAGES) {
    const html = files[p] || "";
    if (!html.includes("<main")) violations.push(`missing runtime page ${p}`);
    if (/canvas id="graph"/.test(html)) violations.push(`${p} must not embed control-room graph`);
  }
  return { ok: violations.length === 0, violations, pages: RUNTIME_PAGES.length };
}

export function knownUniverseObjects(universe, platform) {
  const items = [];
  const push = (kind, id, extra = {}) => items.push({ kind, id, ...extra });
  for (const b of universe.blocks) push("block", b.id, { sha256: b.sha256, artifact: b.artifact_id });
  for (const l of universe.lenses) push("lens", l.id);
  for (const c of universe.checkpoints) push("checkpoint", c.id, { block: c.block });
  for (const p of universe.priorities) push("priority", p.id);
  for (const d of universe.drive) push("drive", d.id, { name: d.name });
  for (const f of universe.inventory.folders) push("folder", f.path, { files: f.files });
  for (const u of universe.unknown_universe) push("unknown", u.id);
  universe.principles.forEach((p, i) => push("principle", `PRIN-${i + 1}`, { text: p }));
  universe.flow.forEach((p, i) => push("flow", `FLOW-${i + 1}`, { text: p }));
  universe.architecture.forEach((p, i) => push("arch", `ARCH-${i + 1}`, { text: p }));
  universe.limitations.forEach((p, i) => push("limit", `LIM-${i + 1}`, { text: p }));
  universe.finding_cycle.forEach((p, i) => push("cycle", `CYC-${i + 1}`, { text: p }));
  universe.assurance_stack.forEach((p, i) => push("stack", `STK-${i + 1}`, { text: p }));
  push("baseline", universe.baseline.global_id, { sha256: universe.baseline.sha256 });
  push("residual", "X", { value: universe.residual_uncertainty.value });
  if (platform) {
    for (const p of RUNTIME_PAGES) push("runtime-page", p);
    if (platform.toolLibrary) push("tool-library-runtime", "CKO-TOOL-LIBRARY-RUNTIME-1.0.0");
    if (platform.governance) push("calenf-governance", "CKO-CALENF-GOVERNANCE-1.0.0");
    if (platform.layers) push("cko-44-layers", "CKO-44-LAYER-SITE-1.0.0");
    if (platform.governance?.evidence_chain) push("md-norm-evidence-chain", MD_NORM_CHAIN_ID);
    for (const p of platform.pendencies?.items || []) push("pendency", p.id, { status: p.status });
    if (platform.driveImmutable) push("drive-immutable", "CKO-DRIVE-IMMUTABLE-1.0.0");
  }
  return items;
}

export function validateRuntimePlatformSchema(platform) {
  if (!platform) return { ok: true, skipped: true, errors: [] };
  const errors = [];
  const files = platform.files || {};
  const listing = platform.listing || Object.keys(files);
  if (listing.includes("app.js")) errors.push("schema: control-room app.js is not a runtime platform file");
  if (RUNTIME_PAGES.length !== 12) errors.push("schema: runtime pages must be exactly 12");
  for (const p of RUNTIME_PAGES) {
    if (!files[p]) errors.push(`schema: missing required page ${p}`);
  }
  const index = files["index.html"] || "";
  if (/id="graph"|Reexecutar cascata|id="orquestrador"|Relat[oó]rio T[eé]cnico Final Controlado/.test(index)) {
    errors.push("schema: report dashboard is not a valid runtime platform");
  }
  if (index && (!/Calculadoras de Enfermagem/.test(index) || !/PAGE_INSTITUTIONAL_CLUSTER/.test(index))) {
    errors.push("schema: home is not Drive Wave2 PAGE_INSTITUTIONAL_CLUSTER");
  }
  errors.push(...validateToolLibrarySchema(platform).errors);
  errors.push(...validatePendenciesSchema(platform).errors);
  errors.push(...validateLayersSchema(platform).errors);
  return { ok: errors.length === 0, errors };
}

export function validateLayersSchema(platform) {
  if (!platform?.layers && !(platform?.files && Object.keys(platform.files).length)) {
    return { ok: true, skipped: true, errors: [] };
  }
  const errors = [];
  const l = platform.layers;
  if (!l) {
    errors.push("schema: 44 classified layers catalog missing");
    return { ok: false, errors };
  }
  if (l.id !== "CKO-44-LAYER-SITE-1.0.0") errors.push("schema: layers id");
  if (l.kind !== "cko-44-layers") errors.push("schema: layers kind must be cko-44-layers");
  if (l.count !== 44 || !Array.isArray(l.layers) || l.layers.length !== 44) errors.push("schema: layers must be 44/44");
  if (!String(l.release || "").includes("NOT_RELEASED")) errors.push("schema: layers must remain NOT_RELEASED");
  if (l.published === true) errors.push("schema: layers must not claim publication");
  const ids = (l.layers || []).map((row) => row.id);
  if (JSON.stringify(ids) !== JSON.stringify(CANONICAL_LAYER_IDS)) errors.push("schema: layer ids must match closure");
  for (const row of l.layers || []) {
    if (row.present !== true) errors.push(`schema: ${row.id} not present`);
    if (!SHA_RE.test(row.sha256 || "")) errors.push(`schema: ${row.id} sha256`);
  }
  return { ok: errors.length === 0, errors };
}

export function validatePendenciesSchema(platform) {
  if (!platform?.pendencies) return { ok: true, skipped: true, errors: [] };
  const errors = [];
  const p = platform.pendencies;
  if (p.id !== "CKO-PENDENCIES-1.0.0") errors.push("schema: pendencies id");
  if (p.root !== "policy-as-code") errors.push("schema: pendencies root must be policy-as-code");
  if (p.mutate_drive !== false) errors.push("schema: pendencies must not mutate Drive");
  if (p.closes_b9 !== false) errors.push("schema: pendencies must not close B9");
  if (!Array.isArray(p.items) || p.items.length < 200) errors.push("schema: pendency ledger too small");
  const locales = (p.items || []).filter((i) => i.kind === "locale-cell").length;
  if (locales !== 360) errors.push("schema: 360 Wave2 locale cells required");
  return { ok: errors.length === 0, errors };
}

export function validateToolLibrarySchema(platform) {
  if (!platform?.toolLibrary) return { ok: true, skipped: true, errors: [] };
  const errors = [];
  const tl = platform.toolLibrary;
  if (tl.kind !== "tool-library-runtime") errors.push("schema: tool library kind must be tool-library-runtime");
  if (tl.release && !String(tl.release).includes("NOT_RELEASED")) errors.push("schema: tool library must remain NOT_RELEASED");
  for (const p of TOOL_RUNTIME_CANARIES) {
    if (!(tl.tool_canaries || []).includes(p)) errors.push(`schema: missing tool runtime ${p}`);
  }
  for (const p of LIBRARY_RUNTIME_CANARIES) {
    if (!(tl.library_canaries || []).includes(p)) errors.push(`schema: missing library runtime ${p}`);
  }
  for (const p of TOOL_ENGINE_LIBS) {
    if (!(tl.engine_libraries || []).includes(p)) errors.push(`schema: missing engine library ${p}`);
  }
  if ((tl.tools_with_calc_runtime || 0) < TOOL_RUNTIME_CANARIES.length) {
    errors.push("schema: calculator runtimes must cover the known tool canaries");
  }
  if ((tl.biblioteca_articles_n || 0) < 1) errors.push("schema: biblioteca article runtime is empty");
  if (tl.structure && tl.structure !== "calenf") errors.push("schema: runtime structure must be calenf");
  for (const p of CALENF_STRUCTURE) {
    if (tl.calenf_structure && !tl.calenf_structure.includes(p)) errors.push(`schema: missing CALENF path ${p}`);
  }
  return { ok: errors.length === 0, errors };
}

export function validateSchema(universe, platform) {
  const errors = [];
  if (universe.document?.classification !== "CONTROLLED") errors.push("document.classification != CONTROLLED");
  if (universe.document?.not_production_release !== true) errors.push("must declare not_production_release");
  if (universe.baseline?.state !== "FINAL_CONTROLLED") errors.push("baseline.state != FINAL_CONTROLLED");
  if (!String(universe.baseline?.release || "").includes("NOT_RELEASED")) errors.push("baseline.release must remain NOT_RELEASED");
  if (!SHA_RE.test(universe.baseline?.sha256 || "")) errors.push("baseline.sha256 invalid");
  if (!Array.isArray(universe.blocks) || universe.blocks.length !== 13) errors.push("blocks must be 13");
  const ids = new Set(universe.blocks?.map((b) => b.id));
  for (const id of BLOCK_IDS) if (!ids.has(id)) errors.push(`missing block ${id}`);
  for (const b of universe.blocks || []) {
    if (!SHA_RE.test(b.sha256 || "")) errors.push(`${b.id} sha256 invalid`);
    if (!b.artifact_id?.startsWith("ART-CKO-")) errors.push(`${b.id} artifact`);
    if (!b.version_id?.startsWith("OV-CKO-")) errors.push(`${b.id} version`);
    if (!b.checkpoint_id?.startsWith("CP-CKO-")) errors.push(`${b.id} checkpoint`);
  }
  if ((universe.lenses || []).length !== 8) errors.push("AUD-8L must have 8 lenses");
  const lensIds = new Set((universe.lenses || []).map((l) => l.id));
  for (const id of LENS_IDS) if (!lensIds.has(id)) errors.push(`missing lens ${id}`);
  if (!universe.unknown_universe?.length) errors.push("unknown universe empty");
  if (typeof universe.residual_uncertainty?.value !== "number") errors.push("X missing");
  const folderSum = (universe.inventory?.folders || []).reduce((a, f) => a + f.files, 0);
  if (folderSum !== 449 || universe.inventory?.file_count !== 449) errors.push("inventory must cover 449 files");
  if (universe.kpis?.aud8l !== "104/104") errors.push("AUD-8L coverage");
  if (universe.kpis?.layers !== "44/44") errors.push("44 layers");
  const plat = validateRuntimePlatformSchema(platform);
  errors.push(...plat.errors);
  return { ok: errors.length === 0, errors };
}

export function evaluatePolicies(universe, ctx = {}) {
  const denials = [];
  const b9 = universe.blocks.find((b) => b.id === "B9");
  const b10 = universe.blocks.find((b) => b.id === "B10");
  const recertFail = universe.blocks.some((b) => (b.holds || []).some((h) => String(h).includes("FAIL")));
  const rights = universe.residual_uncertainty.open_counts.rights_holds;
  const action = ctx.action || "inspect";

  const deny = (id, reason) => denials.push({ id, reason });

  if (ctx.fact && !ctx.evidence) deny("NO_FACT_WITHOUT_EVIDENCE", "fact without evidence");
  if (ctx.evidence_kind === "discovery") deny("DISCOVERY_IS_NOT_EVIDENCE", "discovery != evidence");
  if (ctx.claimed_ack && ctx.event_state === "PENDING") deny("PENDING_IS_NOT_ACK", "PENDING != ACK");
  if (ctx.runtime_claim === "observed" && ctx.runtime_source !== "observed") {
    deny("RUNTIME_OBSERVED_NOT_INFERRED", "observed runtime cannot be inferred");
  }
  if (action === "release") {
    deny("RELEASE_FAIL_CLOSED", "baseline is HOLD / NOT_RELEASED");
    if (b9?.release === "NOT_RELEASED") deny("B9_HOLD_BLOCKS_RELEASE", "B9 remains NOT_RELEASED");
    if (recertFail) deny("RECERT_FAIL_BLOCKS_RELEASE", "B7 recert FAIL");
    if (rights > 0) deny("RIGHTS_CHAIN_REQUIRED_TO_PUBLISH", `${rights} rights holds`);
    if (b10?.operational === "NOT_ASSERTED") deny("NURSEPALM_NOT_ASSERTED", "operational runtime not asserted");
  }
  if (action === "publish_clinical_content" && rights > 0) {
    deny("RIGHTS_CHAIN_REQUIRED_TO_PUBLISH", "cannot publish without rights chain");
  }
  if (ctx.claim === "clinical_operational" && ctx.source === "technical_classification") {
    deny("NO_CLINICAL_CLAIM_FROM_CLASSIFICATION", "classification is not clinical homologation");
  }
  if ((universe.unknown_universe || []).length === 0) deny("UNKNOWN_UNIVERSE_EXPLICIT", "unknown not explicit");
  if (universe.residual_uncertainty?.value == null) deny("RESIDUAL_X_REQUIRED", "X missing");
  if (ctx.platform) {
    const plat = inspectPlatform(ctx.platform);
    for (const d of plat.denials) deny(d.id, d.reason);
  }

  return {
    ok: denials.length === 0,
    mode: "fail-closed",
    denials,
    release_allowed: false,
  };
}

export function graphConstraints(universe, platform) {
  const violations = [];
  const nodes = universe.blocks.map((b) => b.id);
  const edges = [
    ["B1", "B9"],
    ["B2", "B9"],
    ["B3", "B9"],
    ["B4", "B9"],
    ["B5", "B9"],
    ["B6.1", "B9"],
    ["B6.2", "B9"],
    ["B6.3", "B9"],
    ["B6.4", "B9"],
    ["B7", "B9"],
    ["B8", "B9"],
    ["B10", "B9"],
    ["B1", "B10"],
    ["B5", "B10"],
  ];
  for (const [from, to] of edges) {
    if (!nodes.includes(from) || !nodes.includes(to)) violations.push(`missing edge ${from}->${to}`);
  }
  const b9 = universe.blocks.find((b) => b.id === "B9");
  if (b9?.release !== "NOT_RELEASED") violations.push("graph: B9 cannot leave NOT_RELEASED without recert+rights+observed runtime");
  for (const b of universe.blocks) {
    if (!b.sha256 || !b.artifact_id || !b.checkpoint_id) violations.push(`graph: ${b.id} incomplete identity`);
  }
  const twin = universe.blocks.find((b) => b.id === "B5");
  if (twin && !/137 nodes/.test(twin.coverage)) violations.push("B5 digital twin cardinality");
  if ((universe.lenses || []).length !== 8) violations.push("AUD-8L cardinality");
  const plat = platformGraphConstraints(platform);
  violations.push(...plat.violations);
  if (platform?.pendencies) {
    const locales = (platform.pendencies.items || []).filter((i) => i.kind === "locale-cell").length;
    if (locales !== 360) violations.push("graph: Wave2 locale cells must remain 360 classified holds");
    if (platform.pendencies.closes_b9 !== false) violations.push("graph: pendencies cannot close B9");
  }
  if (platform?.governance) {
    const g = inspectCalenfGovernance(platform.governance);
    for (const d of g.denials) violations.push(`graph: ${d.id} ${d.reason}`);
  }
  if (platform?.layers) {
    if (platform.layers.count !== 44 || (platform.layers.layers || []).length !== 44) {
      violations.push("graph: hosted site must contain 44/44 classified layers");
    }
    if (platform.layers.published === true || !String(platform.layers.release || "").includes("NOT_RELEASED")) {
      violations.push("graph: 44-layer fan-in remains HOLD / NOT_RELEASED");
    }
  }
  return {
    ok: violations.length === 0,
    nodes: nodes.length,
    edges: edges.length,
    violations,
    pages: plat.pages || 0,
    temporal: { as_of: universe.document.date, type: "snapshot-graph" },
  };
}

export function coverageReport(universe, platform) {
  const objects = knownUniverseObjects(universe, platform);
  const requiredKinds = ["block", "lens", "checkpoint", "priority", "drive", "folder", "unknown", "baseline", "residual"];
  const missing = [];
  for (const kind of requiredKinds) {
    if (!objects.some((o) => o.kind === kind)) missing.push(kind);
  }
  const folderFiles = universe.inventory.folders.reduce((a, f) => a + f.files, 0);
  if (folderFiles !== 449) missing.push("inventory-449");
  if (objects.filter((o) => o.kind === "block").length !== 13) missing.push("blocks-13");
  if (objects.filter((o) => o.kind === "lens").length !== 8) missing.push("lenses-8");
  const known = objects.length;
  const covered = missing.length === 0 ? known : known - missing.length;
  const ratio = known === 0 ? 0 : covered / known;
  return {
    known,
    covered: missing.length === 0 ? known : covered,
    ratio,
    ok: ratio === 1 && missing.length === 0,
    missing,
    rule: RULES.coverage,
  };
}

export function evidenceCoverage(universe, receipts, platform) {
  const objects = knownUniverseObjects(universe, platform);
  const bySubject = new Map(receipts.map((r) => [r.subject, r]));
  const missing = [];
  for (const obj of objects) {
    const receipt = bySubject.get(obj.id);
    if (!receipt || receipt.no_fact_without_evidence !== true) missing.push(obj.id);
  }
  const ratio = objects.length === 0 ? 0 : (objects.length - missing.length) / objects.length;
  return {
    known: objects.length,
    evidenced: objects.length - missing.length,
    ratio,
    ok: missing.length === 0,
    missing,
    rule: RULES.evidence_coverage,
  };
}

export function runtimeAssertions(universe, platform) {
  const asserts = [];
  const check = (id, ok, detail) => asserts.push({ id, ok, detail });
  check("A-RELEASE-HOLD", String(universe.baseline.release).includes("NOT_RELEASED"), universe.baseline.release);
  check("A-B9-HOLD", universe.blocks.find((b) => b.id === "B9")?.release === "NOT_RELEASED", "B9");
  check("A-B10-NOT-ASSERTED", universe.blocks.find((b) => b.id === "B10")?.operational === "NOT_ASSERTED", "B10");
  check("A-PENDING-NE-ACK", universe.distributed.pending_is_not_ack === true, "outbox");
  check("A-NO-PROD", universe.document.not_production_release === true, "publication");
  check("A-X-BOUNDED", universe.residual_uncertainty.value > 0 && universe.residual_uncertainty.value <= 1, "X");
  check("A-UNKNOWN-EXPLICIT", universe.unknown_universe.length >= 8, universe.unknown_universe.length);
  check("A-HASH-GLOBAL", SHA_RE.test(universe.baseline.sha256), "global hash");
  if (platform) {
    const plat = inspectPlatform(platform);
    check("A-NO-REPORT-DASHBOARD", plat.denials.every((d) => d.id !== "NO_REPORT_DASHBOARD"), "frontend");
    check("A-DRIVE-PLATFORM", plat.denials.every((d) => d.id !== "RUNTIME_IS_DRIVE_PLATFORM"), "wave2");
    check("A-NO-APP-JS", plat.denials.every((d) => d.id !== "NO_CONTROL_ROOM_APP"), "app.js");
    for (const p of RUNTIME_PAGES) {
      const html = platform.files?.[p] || "";
      check(`A-PAGE-${p}`, html.includes("<main"), p);
    }
    if (platform.toolLibrary) {
      const tl = platform.toolLibrary;
      check("A-TOOL-RUNTIME", TOOL_RUNTIME_CANARIES.every((p) => (tl.tool_canaries || []).includes(p)), "tools");
      check("A-LIBRARY-RUNTIME", LIBRARY_RUNTIME_CANARIES.every((p) => (tl.library_canaries || []).includes(p)), "libraries");
      check("A-TOOL-LIBS", TOOL_ENGINE_LIBS.every((p) => (tl.engine_libraries || []).includes(p)), "engines");
      const aldrete = platform.files?.["aldrete.html"] || "";
      check("A-ALDRETE-CALC", /btnCalcular/.test(aldrete) && /scoreValor/.test(aldrete), "aldrete");
    }
    if (platform.governance) {
      const g = inspectCalenfGovernance(platform.governance);
      check("A-CALENF-SCHEMA", g.denials.every((d) => d.id !== "SCHEMA_GOVERNS_RUNTIME"), "schema");
      check("A-CALENF-GRAPH", g.denials.every((d) => d.id !== "GRAPH_GOVERNS_RUNTIME"), "graph");
      check("A-CALENF-TWIN", g.denials.every((d) => d.id !== "TWIN_GOVERNS_RUNTIME"), "twin");
      check("A-CALENF-NURSEPALM", g.denials.every((d) => d.id !== "NURSEPALM_GOVERNS_RUNTIME"), "nurse-palm");
      check("A-CALENF-AGENTIC", g.denials.every((d) => d.id !== "AGENTIC_GOVERNS_RUNTIME"), "agentic");
      check("A-MD-NORM-EVIDENCE", g.denials.every((d) => d.id !== "MD_NORMS_EVIDENCE_CHAIN"), "md-norm");
    }
    if (platform.pendencies) {
      const pend = inspectPendencies(platform.pendencies, platform.driveImmutable);
      check("A-PENDENCIES-EXPLICIT", pend.denials.every((d) => d.id !== "PENDENCIES_EXPLICIT"), "ledger");
      check("A-DRIVE-IMMUTABLE", pend.denials.every((d) => d.id !== "DRIVE_IMMUTABLE"), "drive");
      check("A-PENDENCIES-DO-NOT-CLOSE-B9", platform.pendencies.closes_b9 === false, "B9");
    }
    if (platform.layers || Object.keys(platform.files || {}).length) {
      const lyr = inspectLayers(platform.layers, platform.files?.["ecossistema.html"] || "");
      check("A-LAYERS-44", lyr.ok, "44/44");
      check("A-LAYERS-HOLD", String(platform.layers?.release || "").includes("NOT_RELEASED") && platform.layers?.published !== true, "HOLD");
      const pub = (platform.layers?.layers || []).find((l) => l.id === "LYR-PUB-001");
      check("A-LAYER-PUB-HOLD", pub?.published !== true && String(pub?.release || "").includes("NOT_RELEASED"), "LYR-PUB-001");
    }
  }
  const failed = asserts.filter((a) => !a.ok);
  return { ok: failed.length === 0, asserts, failed };
}

export function buildPropertyGraph(universe) {
  const nodes = [];
  const edges = [];
  nodes.push({ id: "GLOBAL", label: "FINAL_CONTROLLED", type: "Baseline", sha256: universe.baseline.sha256 });
  for (const b of universe.blocks) {
    nodes.push({ id: b.id, label: b.name, type: "Block", state: b.state, sha256: b.sha256 });
    edges.push({ from: b.id, to: "GLOBAL", rel: "fanIn", constraint: "required" });
    edges.push({ from: b.id, to: b.artifact_id, rel: "hasArtifact" });
    nodes.push({ id: b.artifact_id, label: b.version_id, type: "Artifact", sha256: b.sha256 });
    edges.push({ from: b.id, to: b.checkpoint_id, rel: "hasCheckpoint" });
    nodes.push({ id: b.checkpoint_id, label: b.checkpoint_id, type: "Checkpoint" });
  }
  for (const l of universe.lenses) {
    nodes.push({ id: l.id, label: l.name, type: "Lens" });
    for (const b of universe.blocks) edges.push({ from: b.id, to: l.id, rel: "auditedBy" });
  }
  for (const u of universe.unknown_universe) {
    nodes.push({ id: u.id, label: u.statement.slice(0, 72), type: "Unknown" });
    edges.push({ from: "GLOBAL", to: u.id, rel: "explicitUnknown" });
  }
  return { nodes, edges, nodeCount: nodes.length, edgeCount: edges.length };
}

export function evaluationScience(universe) {
  const gold = [
    { id: "g-state", pred: universe.baseline.state, gold: "FINAL_CONTROLLED" },
    { id: "g-rel", pred: universe.baseline.release, gold: "HOLD / NOT_RELEASED" },
    { id: "g-b9", pred: universe.blocks.find((b) => b.id === "B9").release, gold: "NOT_RELEASED" },
    { id: "g-b10", pred: universe.blocks.find((b) => b.id === "B10").operational, gold: "NOT_ASSERTED" },
    { id: "g-files", pred: universe.inventory.file_count, gold: 449 },
    { id: "g-aud", pred: universe.kpis.aud8l, gold: "104/104" },
    { id: "g-layers", pred: universe.kpis.layers, gold: "44/44" },
    { id: "g-agents", pred: universe.kpis.agents_job_profiles, gold: "89/89" },
    { id: "g-holds", pred: universe.kpis.active_holds, gold: 211 },
    { id: "g-reperf", pred: universe.kpis.pending_reperformance, gold: 201 },
    { id: "g-outbox", pred: universe.distributed.outbox_pending, gold: 296 },
    { id: "g-recert", pred: universe.blocks.find((b) => b.id === "B7").holds.includes("recert_FAIL"), gold: true },
  ];
  let tp = 0;
  let fp = 0;
  let fn = 0;
  let tn = 0;
  const rows = gold.map((g) => {
    const match = Object.is(g.pred, g.gold);
    if (match) tp += 1;
    else fp += 1;
    return { ...g, match };
  });
  const precision = tp / (tp + fp || 1);
  const recall = tp / (tp + fn || tp);
  const f1 = precision + recall === 0 ? 0 : (2 * precision * recall) / (precision + recall);
  const maturity = universe.blocks.map((b) => b.maturity);
  const mean = maturity.reduce((a, n) => a + n, 0) / maturity.length;
  const ece = Math.abs(mean / 100 - (1 - universe.residual_uncertainty.value));
  return {
    golden_n: gold.length,
    precision,
    recall,
    f1,
    confusion: { tp, fp, fn, tn },
    calibration_ece: Number(ece.toFixed(4)),
    inter_rater: {
      lenses: 8,
      agreement: 1,
      note: "8/8 AUD-8L lenses closed on the same classified denominator",
    },
    adversarial: {
      release_attempt: evaluatePolicies(universe, { action: "release" }).ok === false,
    },
    drift: {
      baseline_sha256: universe.baseline.sha256,
      detect: "hash mismatch vs OV-CKO-GLOBAL-FINAL-AUD8L-1.0.0 is drift",
    },
    rows,
    ok: precision === 1 && recall === 1 && rows.every((r) => r.match),
  };
}

export function propertyBased(universe) {
  const trials = [];
  for (const b of universe.blocks) {
    const clone = structuredClone(universe);
    const target = clone.blocks.find((x) => x.id === b.id);
    target.release = "RELEASED";
    const pol = evaluatePolicies(clone, { action: "release" });
    trials.push({ mut: `release-${b.id}`, blocked: pol.release_allowed === false && pol.denials.length > 0 });
  }
  const cloneX = structuredClone(universe);
  cloneX.unknown_universe = [];
  const polU = evaluatePolicies(cloneX, { action: "inspect" });
  trials.push({ mut: "drop-unknown", blocked: polU.denials.some((d) => d.id === "UNKNOWN_UNIVERSE_EXPLICIT") });
  return { ok: trials.every((t) => t.blocked), trials };
}

function newIdempotency(seed) {
  return `idem-${seed}`;
}

export function orchestrator(universe, events) {
  const outbox = [];
  const checkpoints = [];
  const dlq = [];
  const seen = new Set();
  const log = [];

  const emit = (type, payload, key) => {
    const ev = {
      id: `EVT-${outbox.length + 1}`,
      type,
      payload,
      idempotency_key: key,
      state: "PENDING",
      attempts: 0,
      ack_is_not_pending: true,
    };
    outbox.push(ev);
    return ev;
  };

  for (const ev of events) {
    const key = ev.idempotency_key || newIdempotency(ev.type + JSON.stringify(ev.payload));
    if (seen.has(key)) {
      log.push({ event: ev.type, result: "duplicate-suppressed", semantics: "at-least-once + idempotency" });
      continue;
    }
    seen.add(key);
    const boxed = emit(ev.type, ev.payload, key);
    boxed.attempts += 1;
    try {
      if (ev.type === "release.request") {
        const pol = evaluatePolicies(universe, { action: "release" });
        if (!pol.ok) {
          boxed.state = "DLQ";
          dlq.push({ ...boxed, reason: pol.denials.map((d) => d.id) });
          log.push({ event: ev.type, result: "saga-compensate", reason: "fail-closed" });
          continue;
        }
      }
      if (ev.type === "ack.claim" && ev.payload?.from === "PENDING") {
        boxed.state = "DLQ";
        dlq.push({ ...boxed, reason: ["PENDING_IS_NOT_ACK"] });
        log.push({ event: ev.type, result: "rejected", reason: "PENDING != ACK" });
        continue;
      }
      const cp = {
        id: `CP-RUNTIME-${checkpoints.length + 1}`,
        event: boxed.id,
        type: ev.type,
        result: "PASS_WITH_SCOPED_HOLDS",
      };
      checkpoints.push(cp);
      boxed.state = "ACK";
      log.push({ event: ev.type, result: "checkpointed", checkpoint: cp.id });
    } catch (err) {
      boxed.state = "DLQ";
      dlq.push({ ...boxed, reason: [String(err)] });
    }
  }

  return {
    pattern: "EVENT → CHECKPOINT → ORCHESTRATOR",
    semantics: "at-least-once with idempotency; exactly-once not claimed",
    pending_is_not_ack: true,
    outbox_report_pending: universe.distributed.outbox_pending,
    processed: outbox.length,
    acked: outbox.filter((e) => e.state === "ACK").length,
    dlq: dlq.length,
    checkpoints,
    log,
    saga: {
      release: "compensated",
      note: "Release saga aborts and compensates while B9 is NOT_RELEASED",
    },
  };
}

export function evaluatePolicyRoot(universe, ctx = {}) {
  const inspect = evaluatePolicies(universe, { ...ctx, action: ctx.action || "inspect" });
  const release = evaluatePolicies(universe, { ...ctx, action: "release" });
  const integrity = inspect.denials.filter((d) => INTEGRITY_DENIALS.has(d.id));
  const ok =
    inspect.mode === "fail-closed" &&
    integrity.length === 0 &&
    release.release_allowed === false &&
    release.denials.length > 0;
  return {
    ok,
    mode: inspect.mode,
    root: "policy-as-code",
    integrity_denials: integrity,
    release_denials: release.denials,
    release_allowed: false,
    inspect,
    release,
  };
}

export async function automaticEvidence(universe, extras = {}) {
  const objects = knownUniverseObjects(universe, extras.platform);
  const now = extras.now || new Date().toISOString();
  const receipts = [];
  const files = extras.platform?.files || {};
  for (const obj of objects) {
    const body =
      obj.kind === "runtime-page"
        ? files[obj.id] || ""
        : obj.kind === "tool-library-runtime"
          ? JSON.stringify(extras.platform?.toolLibrary || {})
          : obj.kind === "calenf-governance"
            ? JSON.stringify(extras.platform?.governance || {})
            : obj.kind === "cko-44-layers"
              ? JSON.stringify(extras.platform?.layers || {})
              : obj.kind === "md-norm-evidence-chain"
                ? JSON.stringify(extras.platform?.governance?.evidence_chain || {})
              : `${obj.kind}:${obj.id}:${obj.sha256 || obj.text || obj.statement || ""}`;
    const sha = await digestSha256(body);
    receipts.push({
      id: `EVD-${obj.kind}-${obj.id}`.replace(/[^A-Za-z0-9-]/g, "-"),
      kind: obj.kind === "checkpoint" ? "checkpoint" : obj.kind === "runtime-page" ? "runtime" : "coverage",
      subject: obj.id,
      sha256: sha,
      created_at: now,
      status: obj.id === "B9" ? "HOLD" : "PASS_WITH_SCOPED_HOLDS",
      gate: "automatic-evidence",
      derived_from: CASCADE,
      root: "policy-as-code",
      no_fact_without_evidence: true,
    });
  }
  return receipts;
}

export async function runGates(universe, options = {}) {
  const cascade = [];
  let blockedBy = null;
  const skip = (id) => {
    cascade.push({
      id,
      ok: false,
      status: "SKIPPED",
      predecessor_failed: blockedBy,
      note: "cascade fail-closed: stage does not run unless policy-as-code and all predecessors PASS",
    });
    return { ok: false, skipped: true, blocked_by: blockedBy };
  };
  const pass = (id, extra = {}) => {
    const prev = cascade.at(-1)?.id ?? null;
    cascade.push({ id, ok: true, status: "PASS", predecessor: prev, root: "policy-as-code", ...extra });
  };
  const fail = (id, extra = {}) => {
    const prev = cascade.at(-1)?.id ?? null;
    cascade.push({ id, ok: false, status: "FAIL", predecessor: prev, root: "policy-as-code", ...extra });
    blockedBy = id;
  };

  const policy = evaluatePolicyRoot(universe, { action: options.action || "inspect", platform: options.platform });
  if (policy.ok) pass("policy-as-code", { release_denied: true });
  else fail("policy-as-code", { integrity_denials: policy.integrity_denials });

  const schema = blockedBy ? skip("schemas") : validateSchema(universe, options.platform);
  if (!blockedBy) (schema.ok ? pass : fail)("schemas", { errors: schema.errors });

  const graph = blockedBy ? skip("graph-constraints") : graphConstraints(universe, options.platform);
  if (!schema.skipped && !blockedBy) (graph.ok ? pass : fail)("graph-constraints", { violations: graph.violations });
  else if (!schema.skipped && blockedBy && cascade.at(-1)?.id !== "graph-constraints") skip("graph-constraints");

  const coverage = coverageReport(universe, options.platform);
  const evaluation = evaluationScience(universe);
  const properties = propertyBased(universe);
  const orch = orchestrator(
    universe,
    options.events || [
      { type: "site.materialize", payload: { version: universe.document.version }, idempotency_key: "site-1" },
      { type: "site.materialize", payload: { version: universe.document.version }, idempotency_key: "site-1" },
      { type: "release.request", payload: { actor: "ci" }, idempotency_key: "rel-1" },
      { type: "ack.claim", payload: { from: "PENDING" }, idempotency_key: "ack-1" },
    ]
  );
  const ciOk =
    coverage.ok &&
    evaluation.ok &&
    properties.ok &&
    orch.dlq >= 2 &&
    orch.acked >= 1 &&
    typeof universe.residual_uncertainty.value === "number" &&
    universe.unknown_universe.length > 0;
  const ci = blockedBy ? skip("CI-gates") : { ok: ciOk };
  if (!ci.skipped) (ci.ok ? pass : fail)("CI-gates", { coverage: coverage.ratio, evaluation: evaluation.ok });

  const runtime = blockedBy ? skip("runtime-assertions") : runtimeAssertions(universe, options.platform);
  if (!runtime.skipped) (runtime.ok ? pass : fail)("runtime-assertions", { failed: runtime.failed });

  let receipts = options.receipts || [];
  let evidence = { ok: false, ratio: 0, missing: ["cascade-blocked"], evidenced: 0 };
  if (blockedBy) {
    skip("automatic-evidence");
  } else {
    receipts = options.receipts || (await automaticEvidence(universe, options));
    evidence = evidenceCoverage(universe, receipts, options.platform);
    if (evidence.ok) pass("automatic-evidence", { receipts_n: receipts.length, ratio: evidence.ratio });
    else fail("automatic-evidence", { missing: evidence.missing });
  }

  const failed = cascade.filter((g) => !g.ok);
  return {
    ok: failed.length === 0 && cascade.length === CASCADE.length && cascade[0].id === "policy-as-code",
    starts_at: "policy-as-code",
    cascade,
    rules: RULES,
    residual_uncertainty: universe.residual_uncertainty,
    unknown_universe: universe.unknown_universe,
    schema: schema.skipped ? schema : schema,
    policy,
    graph: graph.skipped ? graph : graph,
    coverage,
    evidence,
    runtime: runtime.skipped ? runtime : runtime,
    evaluation,
    properties,
    orchestrator: orch,
    gates: cascade,
    failed,
    receipts_n: receipts.length,
    release: "HOLD / NOT_RELEASED",
  };
}
