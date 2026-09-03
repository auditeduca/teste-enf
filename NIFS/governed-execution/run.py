#!/usr/bin/env python3
"""CLI for the CAL-IMC-001 governed execution example."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from kernel.agent import GovernedAgent  # noqa: E402
from kernel.audit import audit_record  # noqa: E402
from kernel.ci import run_ci_gates  # noqa: E402
from kernel.loader import load_object_pack  # noqa: E402
from kernel.models import Actor, ExecutionRequest  # noqa: E402
from kernel.runtime import GovernedRuntime  # noqa: E402
from kernel.scenario import run_imc_scenario  # noqa: E402
from kernel.twin import DigitalTwin  # noqa: E402


def _dump(payload: object) -> None:
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def _actor(value: str) -> Actor:
    kind, _, identifier = value.partition(":")
    if kind not in {"HUMAN", "AGENT"} or not identifier:
        raise SystemExit("actor must be HUMAN:<id> or AGENT:<id>")
    return Actor(type=kind, id=identifier)  # type: ignore[arg-type]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Governed execution kernel — CAL-IMC-001 end-to-end example"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    calc = sub.add_parser("calculate", help="Execute the governed BMI calculator")
    calc.add_argument("--weight", type=float, required=True)
    calc.add_argument("--height", type=float, required=True)
    calc.add_argument("--actor", default="HUMAN:NURSE-001")
    calc.add_argument("--engine", default="DETERMINISTIC_CALC_ENGINE")
    calc.add_argument("--mission", default="Calculate BMI")

    sub.add_parser("ci", help="Run CI promotion gates")
    sub.add_parser("scenario", help="Run the full constitutional scenario")
    sub.add_parser("twin", help="Derive BMI from the sample Digital Twin")
    sub.add_parser("agent-deny", help="Show an agent blocked on invalid input")

    args = parser.parse_args(argv)
    pack = load_object_pack("CAL-IMC-001")

    if args.cmd == "ci":
        _dump(run_ci_gates(pack))
        return 0 if run_ci_gates(pack)["status"] == "DEPLOYABLE" else 1

    if args.cmd == "scenario":
        _dump(run_imc_scenario())
        return 0

    runtime = GovernedRuntime(pack)

    if args.cmd == "calculate":
        result = runtime.execute(
            ExecutionRequest(
                calculator_id="CAL-IMC-001",
                version="1.0.0",
                input={"weight_kg": args.weight, "height_m": args.height},
                actor=_actor(args.actor),
                engine=args.engine,
                mission=args.mission,
            )
        )
        _dump(audit_record(result))
        return 0 if result.executed else 2

    if args.cmd == "twin":
        twin = DigitalTwin(pack.twin_contract["seed_state"], pack)
        result = twin.derive(runtime)
        _dump(
            {
                "twin_event": result.twin_event,
                "execution": audit_record(result),
                "knowledge_graph": twin.knowledge_graph(result),
            }
        )
        return 0 if result.executed else 2

    if args.cmd == "agent-deny":
        agent = GovernedAgent(pack, runtime)
        result = agent.invoke("Calcule o IMC desse paciente.", {"weight_kg": 70, "height_m": 0})
        _dump(audit_record(result))
        return 0 if result.status == "DENIED" else 1

    raise SystemExit(f"unknown command {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
