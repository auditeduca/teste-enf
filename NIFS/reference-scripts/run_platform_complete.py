#!/usr/bin/env python3
"""Comando único — inventário, parada de agentes e conclusão da plataforma.

Para o que estiver rodando, levanta pendências reais e executa os pipelines
na ordem correta (determinístico por padrão; LLM só com --llm + API key).

Uso:
  python scripts/run_platform_complete.py --inventory
  python scripts/run_platform_complete.py --stop-agents
  python scripts/run_platform_complete.py --all
  python scripts/run_platform_complete.py --all --llm --build --ci
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
REPORT_PATH = ROOT / "datasets" / "metadata" / "platform_complete_report.json"

AGENT_CMD_RE = re.compile(
    r"run_batch|run_phases|run_field_pipeline|run_site_full|run_resources|"
    r"run_global|run_careers|run_code_review|content_agents|apgar_agents",
    re.I,
)
KEEP_CMD_RE = re.compile(r"nkp_api\.py|serve_website|http\.server", re.I)

NOW = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _py(*parts: str) -> list[str]:
    return [sys.executable, str(SCRIPTS / parts[0])] + list(parts[1:])


def _run_step(name: str, cmd: list[str], *, timeout: int | None = None) -> dict[str, Any]:
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        ok = proc.returncode == 0
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
    except subprocess.TimeoutExpired as exc:
        ok = False
        out = (exc.stdout or "")[-2000:] if exc.stdout else ""
        err = f"timeout after {timeout}s"
        proc = None
    elapsed = round(time.monotonic() - t0, 1)
    return {
        "step": name,
        "ok": ok,
        "exit_code": proc.returncode if proc else -1,
        "elapsed_s": elapsed,
        "cmd": " ".join(cmd),
        "stdout_tail": "\n".join(out.splitlines()[-8:]),
        "stderr_tail": "\n".join(err.splitlines()[-8:]),
    }


def stop_agents(*, api_url: str = "http://127.0.0.1:8787") -> dict[str, Any]:
    """Para revisão LangGraph na API e processos Python de agentes."""
    stopped: list[dict[str, Any]] = []

    # API review stop
    try:
        req = urllib.request.Request(
            f"{api_url}/api/review/stop",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode())
        stopped.append({"target": "review_api", "ok": True, "detail": body})
    except urllib.error.URLError as exc:
        stopped.append({"target": "review_api", "ok": False, "detail": str(exc)})

    # Windows: encerrar processos agente (preserva API e serve website)
    if sys.platform == "win32":
        ps = (
            "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
            "Where-Object { $_.CommandLine -match 'run_batch|run_phases|run_field_pipeline|"
            "run_site_full|run_resources|run_global|run_careers|run_code_review' "
            "-and $_.CommandLine -notmatch 'nkp_api|serve_website' } | "
            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; "
            "$_.ProcessId }"
        )
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        pids = [x.strip() for x in (proc.stdout or "").splitlines() if x.strip().isdigit()]
        stopped.append({"target": "python_agents", "ok": True, "pids": pids})
    else:
        proc = subprocess.run(["pgrep", "-af", "python"], capture_output=True, text=True)
        pids = []
        for line in (proc.stdout or "").splitlines():
            if AGENT_CMD_RE.search(line) and not KEEP_CMD_RE.search(line):
                pid = line.split(None, 1)[0]
                subprocess.run(["kill", "-TERM", pid], check=False)
                pids.append(pid)
        stopped.append({"target": "python_agents", "ok": True, "pids": pids})

    return {"stopped_at": NOW(), "actions": stopped}


def repair_datasets() -> dict[str, Any]:
    """Repara JSON truncado/duplicado (ex.: medication_dictionary)."""
    fixes = []
    med = ROOT / "datasets" / "clinical" / "medication_dictionary.json"
    if med.is_file():
        text = med.read_text(encoding="utf-8")
        try:
            json.loads(text)
            fixes.append({"file": str(med.relative_to(ROOT)), "action": "ok"})
        except json.JSONDecodeError:
            obj, _ = json.JSONDecoder().raw_decode(text)
            obj["count"] = len(obj.get("records", []))
            med.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            fixes.append({"file": str(med.relative_to(ROOT)), "action": "repaired", "records": obj["count"]})
    return {"fixes": fixes}


def inventory(*, refresh: bool = True) -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    from agent_common.pending_inventory import collect as pending_collect  # noqa: WPS433
    from monitor_progress import collect  # noqa: WPS433

    snap = collect(refresh_resource=refresh)
    pending = pending_collect()

    return {
        "generated_at": NOW(),
        "snapshot": snap,
        "pending": pending,
        "pending_summary": [
            f"{a['agent']}: {a.get('pending', a.get('pending_pct', '?'))}"
            for a in pending.get("actions", [])
        ],
        "all_complete": len(pending.get("actions", [])) == 0,
    }


def run_all(
    *,
    use_llm: bool = False,
    build: bool = False,
    ci: bool = False,
    wrapup: bool = False,
    med_dict_limit: int = 500,
    asset_limit: int = 851,
    bulk_limit: int = 20,
) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []

    def step(name: str, cmd: list[str], timeout: int | None = None) -> bool:
        r = _run_step(name, cmd, timeout=timeout)
        steps.append(r)
        mark = "OK" if r["ok"] else "FAIL"
        print(f"  [{mark}] {name} ({r['elapsed_s']}s)")
        if not r["ok"] and r.get("stderr_tail"):
            print(f"       {r['stderr_tail'][:200]}")
        return r["ok"]

    llm_flag = ["--llm"] if use_llm else ["--no-llm"]

    print("=== 1/12 Parar agentes ===")
    stop_report = stop_agents()
    steps.append({"step": "stop_agents", "ok": True, "detail": stop_report})

    print("=== 2/12 Reparar datasets ===")
    repair = repair_datasets()
    steps.append({"step": "repair_datasets", "ok": True, "detail": repair})

    print("=== 3/12 Content Factory sync ===")
    step("content_factory_sync", _py("content_factory_sync.py", "--country", "BR"))

    print("=== 4/12 Resource expansion ===")
    step(
        "resource_expansion",
        _py(
            "resource_expansion_agents/run_resources.py",
            "--all",
            "--limit",
            str(asset_limit),
            "--med-dict-limit",
            "0",
            *llm_flag,
        ),
        timeout=3600,
    )

    print("=== 5/12 Dicionário medicamentos (fila completa) ===")
    med_limit = str(med_dict_limit) if med_dict_limit > 0 else "all"
    med_cmd = _py("medication_dictionary_agents/run_batch.py", *(["--all-pending"] if med_dict_limit <= 0 else ["--limit", str(med_dict_limit)]))
    if use_llm:
        med_cmd.append("--llm")
    step("medication_dictionary", med_cmd, timeout=7200)

    print("=== 5b/12 Retry workflows content-pending ===")
    step("workflow_retry", _py("content/workflow_runner.py", "--retry-failed", "--limit", "20", *(["--no-llm"] if not use_llm else [])), timeout=600)

    print("=== 6/12 Notificações compulsórias ===")
    step(
        "compulsory_scrape",
        _py("compulsory_notification_agents/run_batch.py", "--scrape", "--scrape-limit", "50"),
        timeout=600,
    )
    step("compulsory_validate", _py("compulsory_notification_agents/run_batch.py", "--validate"))

    print("=== 7/12 Legislação brasileira ===")
    step(
        "legislation_refresh",
        _py("brazilian_legislation_agents/run_batch.py", "--refresh", "--all-sources"),
        timeout=900,
    )
    step("legislation_validate", _py("brazilian_legislation_agents/run_batch.py", "--validate"))

    print("=== 7b/14 ANVISA dados abertos (mensal) ===")
    anv_ssl = ["--no-ssl-verify"] if sys.platform == "win32" else []
    step(
        "anvisa_open_data",
        _py("anvisa_open_data_agents/run_batch.py", "--monthly", "--limit", "5", *anv_ssl),
        timeout=3600,
    )

    print("=== 8/14 Expansão global ===")
    step(
        "global_expansion",
        _py("global_expansion_agents/run_global.py", "--all", "--rebuild", *llm_flag),
        timeout=1800,
    )

    print("=== 9/14 Carreiras ===")
    step("careers", _py("career_agents/run_careers.py", "--all", *llm_flag), timeout=600)

    print("=== 10/14 Site Full (M01–M18) ===")
    site_cmd = _py(
        "site_agents/run_site_full.py",
        "--all",
        "--approve",
        "--bulk-limit",
        str(bulk_limit),
        *llm_flag,
    )
    if build:
        site_cmd.append("--build")
    else:
        site_cmd.append("--no-build")
    step("site_full", site_cmd, timeout=3600)

    print("=== 11/14 Validação conteúdo pendente ===")
    step("content_pending_validate", _py("content/validate_content.py"))

    if ci:
        print("=== 12/13 CI gate ===")
        step("ci", _py("run_ci.py", "--pt-only"), timeout=3600)
    else:
        steps.append({"step": "ci", "ok": True, "skipped": True})

    if wrapup:
        print("=== 13/13 Wrap-up (auditoria + minify + i18n) ===")
        step(
            "project_wrapup",
            _py("run_project_wrapup.py", "--skip-anvisa", *(["--skip-build"] if build else [])),
            timeout=10800,
        )

    print("=== Inventário final ===")
    inv_after = inventory(refresh=True)

    ok_count = sum(1 for s in steps if s.get("ok") and not s.get("skipped"))
    fail_count = sum(1 for s in steps if s.get("ok") is False)

    report = {
        "schema_version": "2026.2.10-platform-complete",
        "generated_at": NOW(),
        "ok": fail_count == 0,
        "steps_ok": ok_count,
        "steps_fail": fail_count,
        "use_llm": use_llm,
        "inventory_after": inv_after,
        "steps": steps,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(REPORT_PATH.relative_to(ROOT))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventário + conclusão única da plataforma NKOS")
    parser.add_argument("--inventory", action="store_true", help="Só inventário de pendências")
    parser.add_argument("--stop-agents", action="store_true", help="Só parar agentes")
    parser.add_argument("--all", action="store_true", help="Executar pipeline completo")
    parser.add_argument("--llm", action="store_true", help="Usar DeepSeek onde disponível")
    parser.add_argument("--build", action="store_true", help="Incluir build website (M18)")
    parser.add_argument("--ci", action="store_true", help="Rodar run_ci.py ao final")
    parser.add_argument("--pending", action="store_true", help="Só agentes com pendências (run_pending_agents)")
    parser.add_argument("--med-dict-limit", type=int, default=0, help="Lote DICT (0=toda fila)")
    parser.add_argument("--asset-limit", type=int, default=851)
    parser.add_argument("--wrapup", action="store_true", help="Auditoria + minify CSS + rebuild i18n")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.stop_agents:
        result = stop_agents()
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"Agentes parados: {result}")
        return 0

    if args.pending:
        from run_pending_agents import run_pending  # noqa: WPS433

        report = run_pending(use_llm=args.llm)
        return 0 if report.get("ok") else 1

    if args.inventory or not args.all:
        inv = inventory(refresh=True)
        if args.json:
            print(json.dumps(inv, ensure_ascii=False, indent=2))
        else:
            print(f"=== Inventário @ {inv['generated_at']} ===")
            snap = inv["snapshot"]
            for name, prog in snap.get("programs", {}).items():
                if "completion_pct" in prog:
                    print(f"  {name:22} {prog['completion_pct']}%")
                elif "status" in prog:
                    print(f"  {name:22} {prog['status']}")
            if inv["pending_summary"]:
                print("\nPendências (agentes):")
                for line in inv["pending_summary"]:
                    print(f"  • {line}")
            elif inv.get("pending", {}).get("actions"):
                print("\nPendências (agentes):")
                for a in inv["pending"]["actions"]:
                    print(f"  • {a['agent']}: {a.get('pending', a.get('pending_pct', '?'))}")
            else:
                print("\nNenhuma pendência crítica detectada.")
            print(f"\nArtefato: datasets/metadata/progress_monitor.json")
            if not args.all:
                print("\nPara concluir pendências: python scripts/run_pending_agents.py --run")
                print("Pipeline completo: python scripts/run_platform_complete.py --all [--ci]")
        return 0 if inv.get("all_complete") else 1

    report = run_all(
        use_llm=args.llm,
        build=args.build,
        ci=args.ci,
        wrapup=args.wrapup,
        med_dict_limit=args.med_dict_limit,
        asset_limit=args.asset_limit,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"\n=== Platform Complete: {'PASS' if report['ok'] else 'FAIL'} ===")
        print(f"Steps OK: {report['steps_ok']} | FAIL: {report['steps_fail']}")
        print(f"Relatório: {report['report_path']}")
        pending = report["inventory_after"].get("pending_summary", [])
        if pending:
            print("Pendências restantes:")
            for line in pending:
                print(f"  • {line}")
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
