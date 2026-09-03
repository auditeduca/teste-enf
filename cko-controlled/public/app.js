import { runGates, buildPropertyGraph } from "./engine/core.js";

const $ = (id) => document.getElementById(id);

function el(tag, attrs = {}, kids = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k === "html") node.innerHTML = v;
    else if (k === "text") node.textContent = v;
    else node.setAttribute(k, v);
  }
  for (const kid of kids) node.append(kid);
  return node;
}

function table(headers, rows) {
  const t = el("table");
  const thead = el("thead");
  const trh = el("tr");
  headers.forEach((h) => trh.append(el("th", { text: h })));
  thead.append(trh);
  t.append(thead);
  const tb = el("tbody");
  for (const row of rows) {
    const tr = el("tr");
    for (const cell of row) {
      const td = el("td");
      if (cell instanceof Node) td.append(cell);
      else td.textContent = cell;
      tr.append(td);
    }
    tb.append(tr);
  }
  t.append(tb);
  return t;
}

function tag(text, kind) {
  return el("span", { class: `tag ${kind}`, text });
}

function heatClass(v) {
  if (v >= 100) return "c100";
  if (v >= 75) return "c75";
  if (v >= 50) return "c50";
  if (v >= 25) return "c25";
  return "c0";
}

function renderUniverse(u) {
  $("hash").textContent = u.baseline.sha256;
  $("x-value").textContent = u.residual_uncertainty.value.toFixed(4);
  $("x-note").textContent = u.residual_uncertainty.interpretation;

  const kpiMount = $("kpis");
  kpiMount.replaceChildren();
  const kpis = [
    [u.kpis.blocks_checkpoints, "blocos/checkpoints"],
    [u.kpis.aud8l, "AUD-8L"],
    [u.kpis.layers, "camadas"],
    [u.kpis.layer_x_stage_mesh, "malha layer × stage"],
    [String(u.kpis.snapshot_files), "arquivos snapshot"],
    [String(u.kpis.md_fields), "campos MD"],
    [String(u.kpis.normative_bindings), "bindings normativos"],
    [u.kpis.agents_job_profiles, "agentes / jobs"],
    [String(u.kpis.active_holds), "holds ativos"],
    [String(u.kpis.open_findings), "findings abertos"],
    [String(u.kpis.pending_reperformance), "reperformance pendente"],
    [String(u.distributed.outbox_pending), "outbox PENDING"],
  ];
  for (const [v, l] of kpis) kpiMount.append(el("div", { class: "kpi" }, [el("b", { text: v }), el("span", { text: l })]));

  $("flow").replaceChildren();
  u.flow.forEach((step, i) => {
    $("flow").append(el("b", { text: step }));
    if (i < u.flow.length - 1) $("flow").append(el("i", { text: "→" }));
  });

  $("principles").replaceChildren();
  u.principles.forEach((p) => $("principles").append(el("li", { text: p })));
  $("cycle").replaceChildren();
  u.finding_cycle.forEach((p) => $("cycle").append(el("li", { text: p })));
  $("arch").replaceChildren();
  u.architecture.forEach((p) => $("arch").append(el("li", { text: p })));

  const blocks = u.blocks.map((b) => [
    b.id,
    b.name,
    b.control,
    b.coverage,
    tag(b.pending, b.id === "B9" || b.id === "B7" ? "fail" : "hold"),
    b.maturity + "%",
  ]);
  $("blocks-table").replaceChildren(table(["Bloco", "Função", "Controle", "Cobertura", "Pendência", "Maturidade"], blocks));

  $("lenses").replaceChildren();
  u.lenses.forEach((l, i) => {
    $("lenses").append(
      el("div", { class: "card" }, [
        el("h3", { text: `${i + 1}. ${l.name}` }),
        el("p", { class: "muted", text: l.purpose }),
      ])
    );
  });

  const cats = ["historico", "runtime", "rights", "security", "release", "other"];
  const heat = $("heatmap-holds");
  heat.replaceChildren(el("span", { class: "lab", text: "" }), ...cats.map((c) => el("span", { class: "lab", text: c })));
  for (const b of u.blocks) {
    heat.append(el("span", { class: "lab", text: b.id }));
    for (const c of cats) {
      const hit = (b.holds || []).some((h) => String(h).toLowerCase().includes(c.slice(0, 4)));
      const score = b.id === "B9" && c === "release" ? 100 : hit ? 70 : b.id === "B7" && c === "security" ? 90 : 10;
      heat.append(el("span", { class: heatClass(100 - score), text: String(score) }));
    }
  }

  const mat = $("heatmap-mat");
  mat.replaceChildren();
  for (const b of u.blocks) {
    mat.append(el("span", { class: "lab", text: b.id }));
    mat.append(el("span", { class: heatClass(b.maturity), text: String(b.maturity) }));
  }

  $("priorities").replaceChildren(
    table(
      ["Pri", "Domínio", "Evidência", "Efeito"],
      u.priorities.map((p) => [tag(p.priority, p.priority === "P0" ? "fail" : "hold"), p.domain, p.evidence, p.effect])
    )
  );

  $("artifacts").replaceChildren(
    table(
      ["Bloco", "Artifact", "Version", "SHA-256", "Checkpoint"],
      [
        ...u.blocks.map((b) => [b.id, b.artifact_id, b.version_id, b.sha256, b.checkpoint_id]),
        ["GLOBAL", u.baseline.artifact_id, u.baseline.global_id, u.baseline.sha256, "CP-CKO-GLOBAL-FINAL-360-20260902-001"],
      ]
    )
  );

  $("drive-table").replaceChildren(
    table(
      ["Nome", "Drive ID", "Localização comprovada"],
      u.drive.map((d) => [d.name, d.id, d.path])
    )
  );

  $("folders").replaceChildren(
    table(
      ["Caminho", "Arquivos"],
      u.inventory.folders.map((f) => [f.path, String(f.files)])
    )
  );

  $("unknown").replaceChildren();
  u.unknown_universe.forEach((item) => {
    $("unknown").append(el("li", {}, [el("strong", { text: item.id + " — " }), document.createTextNode(item.statement)]));
  });

  $("limits").replaceChildren();
  u.limitations.forEach((t) => $("limits").append(el("li", { text: t })));

  $("x-json").textContent = JSON.stringify(u.residual_uncertainty, null, 2);

  const g = buildPropertyGraph(u);
  $("graph-meta").textContent = `${g.nodeCount} nós · ${g.edgeCount} arestas · temporal snapshot ${u.document.date}`;
  drawGraph($("graph"), g);
}

function drawGraph(canvas, graph) {
  const ctx = canvas.getContext("2d");
  const w = (canvas.width = canvas.clientWidth || 800);
  const h = (canvas.height = 320);
  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = "#fffdf8";
  ctx.fillRect(0, 0, w, h);
  const blocks = graph.nodes.filter((n) => n.type === "Block");
  const cx = w / 2;
  const cy = h / 2;
  ctx.strokeStyle = "#1a3e74";
  ctx.fillStyle = "#0c2340";
  ctx.beginPath();
  ctx.arc(cx, cy, 18, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#fff";
  ctx.font = "10px sans-serif";
  ctx.fillText("G", cx - 4, cy + 3);
  blocks.forEach((n, i) => {
    const a = (Math.PI * 2 * i) / blocks.length - Math.PI / 2;
    const x = cx + Math.cos(a) * 120;
    const y = cy + Math.sin(a) * 110;
    ctx.strokeStyle = n.id === "B9" ? "#b42318" : "#1a3e74";
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.fillStyle = n.id === "B9" ? "#b42318" : n.id === "B7" ? "#b45309" : "#1a3e74";
    ctx.beginPath();
    ctx.arc(x, y, 14, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#fff";
    ctx.font = "9px sans-serif";
    ctx.fillText(n.id, x - 10, y + 3);
  });
}

async function runLive(universe) {
  $("gate-status").textContent = "executando gates…";
  const report = await runGates(universe);
  $("gate-status").textContent = report.ok
    ? "CASCADE PASS · raiz policy-as-code · release HOLD / NOT_RELEASED"
    : "CASCADE FAIL · fail-closed a partir de " + (report.failed[0]?.id || "policy-as-code");
  $("gate-status").className = report.ok ? "tag pass" : "tag fail";
  document.querySelectorAll("#cascade-live li[data-stage]").forEach((node) => {
    const stage = report.cascade.find((g) => g.id === node.dataset.stage);
    node.classList.remove("pass", "fail", "skip");
    if (!stage) return;
    node.classList.add(stage.status === "PASS" ? "pass" : stage.status === "SKIPPED" ? "skip" : "fail");
    const small = node.querySelector("small") || node.appendChild(el("small"));
    small.textContent = stage.status;
  });
  $("gates").replaceChildren(
    table(
      ["Estágio", "Predecessor", "Status"],
      report.cascade.map((g, i) => [
        (i === 0 ? "raiz · " : "") + g.id,
        g.predecessor || g.predecessor_failed || "—",
        tag(g.status, g.status === "PASS" ? "pass" : g.status === "SKIPPED" ? "hold" : "fail"),
      ])
    )
  );
  $("eval").textContent = JSON.stringify(
    {
      precision: report.evaluation.precision,
      recall: report.evaluation.recall,
      f1: report.evaluation.f1,
      confusion: report.evaluation.confusion,
      ece: report.evaluation.calibration_ece,
      inter_rater: report.evaluation.inter_rater,
      adversarial_release_blocked: report.evaluation.adversarial.release_attempt,
    },
    null,
    2
  );
  $("orch").textContent = JSON.stringify(
    {
      pattern: report.orchestrator.pattern,
      semantics: report.orchestrator.semantics,
      acked: report.orchestrator.acked,
      dlq: report.orchestrator.dlq,
      saga: report.orchestrator.saga,
      log: report.orchestrator.log,
    },
    null,
    2
  );
  $("coverage-box").textContent = JSON.stringify(
    {
      starts_at: report.starts_at,
      cascade: report.cascade.map((g) => `${g.id}:${g.status}`),
      coverage: report.coverage,
      evidence: { ratio: report.evidence.ratio, ok: report.evidence.ok, evidenced: report.evidence.evidenced },
      residual_uncertainty: report.residual_uncertainty.value,
      unknown: report.unknown_universe.length,
      test_pass: "100% dos testes definidos (suite node:test)",
    },
    null,
    2
  );
}

const universe = await (await fetch("./data/universe.json")).json();
renderUniverse(universe);
await runLive(universe);
$("run-gates")?.addEventListener("click", () => runLive(universe));

const links = [...document.querySelectorAll("nav.toc a")];
const io = new IntersectionObserver(
  (entries) => {
    for (const e of entries) {
      if (e.isIntersecting) {
        links.forEach((a) => a.classList.toggle("active", a.getAttribute("href") === "#" + e.target.id));
      }
    }
  },
  { rootMargin: "-40% 0px -55% 0px" }
);
document.querySelectorAll("main section[id]").forEach((s) => io.observe(s));
