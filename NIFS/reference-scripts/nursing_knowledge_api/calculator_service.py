"""Calculator service — executable calculations for third-party embed."""
from __future__ import annotations

import math


def calc_drip_rate(*, volume: float, time: float, factor: float = 20, time_unit: str = "hours") -> dict:
    if volume <= 0 or time <= 0 or factor <= 0:
        return {"ok": False, "error": "invalid_input", "message": "volume, time and factor must be positive"}
    time_min = time * 60 if time_unit == "hours" else time
    gtt = (volume * factor) / time_min
    mlh = (volume / time_min) * 60
    drops = round(gtt)
    return {
        "ok": True,
        "drops_per_minute": drops,
        "ml_per_hour": round(mlh, 1),
        "formula": "(volume × factor) ÷ time_minutes",
        "inputs": {"volume_ml": volume, "time": time, "time_unit": time_unit, "factor": factor},
    }


def calc_bmi(*, weight_kg: float, height_m: float | None = None, height_cm: float | None = None) -> dict:
    if height_cm and not height_m:
        height_m = height_cm / 100
    if not height_m or height_m <= 0 or weight_kg <= 0:
        return {"ok": False, "error": "invalid_input"}
    bmi = weight_kg / (height_m ** 2)
    band = "normal"
    if bmi < 18.5:
        band = "underweight"
    elif bmi >= 25:
        band = "overweight" if bmi < 30 else "obesity"
    return {
        "ok": True,
        "bmi": round(bmi, 1),
        "classification": band,
        "inputs": {"weight_kg": weight_kg, "height_m": height_m},
    }


def calc_fluid_balance(*, intake_ml: float, output_ml: float) -> dict:
    balance = intake_ml - output_ml
    return {
        "ok": True,
        "balance_ml": round(balance, 1),
        "intake_ml": intake_ml,
        "output_ml": output_ml,
        "status": "positive" if balance > 0 else ("negative" if balance < 0 else "neutral"),
    }


def run_calculator(calc_id: str, params: dict) -> dict:
    cid = calc_id.lower().replace("-", "_")
    if cid in ("drip_rate", "drip-rate", "infusion", "gotejamento"):
        return calc_drip_rate(
            volume=float(params.get("volume") or params.get("volume_ml", 0)),
            time=float(params.get("time") or params.get("time_hours") or params.get("time_min", 0)),
            factor=float(params.get("factor") or params.get("drop_factor", 20)),
            time_unit=params.get("time_unit") or ("minutes" if params.get("time_min") else "hours"),
        )
    if cid == "bmi":
        return calc_bmi(
            weight_kg=float(params.get("weight_kg") or params.get("weight", 0)),
            height_m=params.get("height_m"),
            height_cm=params.get("height_cm"),
        )
    if cid in ("fluid_balance", "fluid-balance", "balanco_hidrico"):
        return calc_fluid_balance(
            intake_ml=float(params.get("intake_ml") or params.get("intake", 0)),
            output_ml=float(params.get("output_ml") or params.get("output", 0)),
        )
    return {"ok": False, "error": "calculator_not_implemented", "calculator_id": calc_id}
