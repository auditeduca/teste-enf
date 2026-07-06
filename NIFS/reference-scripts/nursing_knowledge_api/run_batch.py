"""CLI — Nursing Knowledge API smoke tests."""
from __future__ import annotations

import argparse
import json

from calculator_service import calc_drip_rate
from clinical_service import get_scale
from status import collect_status


def main() -> None:
    p = argparse.ArgumentParser(description="Nursing Knowledge API")
    p.add_argument("--status", action="store_true")
    p.add_argument("--scale", default="braden")
    p.add_argument("--drip", action="store_true")
    args = p.parse_args()

    if args.status:
        print(json.dumps(collect_status(), ensure_ascii=False, indent=2))
        return
    if args.drip:
        print(json.dumps(calc_drip_rate(volume=500, time=4, factor=20), ensure_ascii=False, indent=2))
        return
    print(json.dumps(get_scale(args.scale), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
