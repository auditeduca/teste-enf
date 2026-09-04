#!/usr/bin/env python3
"""Desktop HTTP console for CAL-IMC-001 governed execution."""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kernel.agent import GovernedAgent
from kernel.audit import audit_record, drift_report
from kernel.ci import run_ci_gates
from kernel.loader import load_object_pack
from kernel.models import Actor, ExecutionRequest
from kernel.runtime import GovernedRuntime
from kernel.twin import DigitalTwin

PACK = load_object_pack("CAL-IMC-001")
RUNTIME = GovernedRuntime(PACK)
STATIC = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8090


def _json_response(handler: BaseHTTPRequestHandler, payload: object, status: int = 200) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length else b"{}"
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def _envelope(result) -> dict:
    evidence = result.evidence or {}
    return {
        "status": result.status,
        "decision": result.decision.status,
        "reason": result.decision.reason,
        "failed_rule": result.decision.failed_rule,
        "failed_assertion": result.decision.failed_assertion,
        "execution": audit_record(result),
        "evidence": evidence,
        "provenance": result.provenance,
        "twin_event": result.twin_event,
        "drift": drift_report(RUNTIME.executions),
        "log_size": len(RUNTIME.executions),
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            html = (STATIC / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(html)
            return
        if path == "/api/ci":
            _json_response(self, run_ci_gates(PACK))
            return
        if path == "/api/status":
            _json_response(
                self,
                {
                    "object_id": PACK.canonical["canonical_id"],
                    "version": PACK.canonical["version"],
                    "policy": PACK.policy["id"],
                    "executions": len(RUNTIME.executions),
                },
            )
            return
        self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            payload = _read_json(self)
        except json.JSONDecodeError:
            _json_response(self, {"error": "invalid_json"}, 400)
            return
        if path == "/api/calculate":
            actor_type = payload.get("actor_type", "HUMAN")
            actor_id = payload.get("actor_id") or ("NURSE-001" if actor_type == "HUMAN" else "AGENT-NURSE-001")
            request = ExecutionRequest(
                calculator_id="CAL-IMC-001",
                version="1.0.0",
                input={
                    "weight_kg": payload.get("weight_kg"),
                    "height_m": payload.get("height_m"),
                },
                actor=Actor(type=actor_type, id=actor_id),
                engine=payload.get("engine", "DETERMINISTIC_CALC_ENGINE"),
                mission=payload.get("mission", "Calculate BMI"),
            )
            result = RUNTIME.execute(request)
            _json_response(self, _envelope(result))
            return
        if path == "/api/agent":
            agent = GovernedAgent(PACK, RUNTIME)
            result = agent.invoke(
                payload.get("mission", "Calcule o IMC desse paciente."),
                {
                    "weight_kg": payload.get("weight_kg"),
                    "height_m": payload.get("height_m"),
                },
                engine=payload.get("engine", "DETERMINISTIC_CALC_ENGINE"),
            )
            body = _envelope(result)
            body["mutation"] = {
                "target": "policy",
                "decision": agent.attempt_mutation("policy").status,
                "reason": agent.attempt_mutation("policy").reason,
            }
            _json_response(self, body)
            return
        if path == "/api/twin":
            twin = DigitalTwin(PACK.twin_contract["seed_state"], PACK)
            result = twin.derive(RUNTIME, actor=Actor(type="AGENT", id="AGENT-NURSE-001"))
            body = _envelope(result)
            body["knowledge_graph"] = twin.knowledge_graph(result)
            _json_response(self, body)
            return
        self.send_error(404)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"CAL-IMC-001 desktop console → http://{HOST}:{PORT}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
