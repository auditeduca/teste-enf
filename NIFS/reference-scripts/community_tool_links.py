"""Shared mappings: community entities → clinical tool codes."""
from __future__ import annotations

FORUM_SPECIALTY_TOOLS: dict[str, list[str]] = {
    "uti": ["TOOL.RASS", "TOOL.CAM-ICU", "TOOL.SOFA", "TOOL.APACHE2"],
    "emergencia": ["TOOL.NEWS2", "TOOL.MEWS", "TOOL.GCS", "TOOL.qSOFA"],
    "sae": ["TOOL.BRADEN", "TOOL.GCS", "TOOL.MORSE"],
    "farmaco": ["TOOL.INFUSION", "TOOL.INSULIN", "TOOL.9RIGHTS", "TOOL.HEPARIN"],
    "pediatria": ["TOOL.APGAR", "TOOL.BALLARD", "TOOL.BMI"],
    "obstetricia": ["TOOL.APGAR", "TOOL.BALLARD"],
    "geriatria": ["TOOL.BARTHEL", "TOOL.KATZ", "TOOL.MORSE", "TOOL.BRADEN"],
    "saude-mental": ["TOOL.GCS", "TOOL.RASS", "TOOL.CAM-ICU"],
    "feridas": ["TOOL.BRADEN", "TOOL.NORTON", "TOOL.WATERLOW"],
    "gestao": ["TOOL.TURNOVER"],
    "concursos": ["TOOL.GCS", "TOOL.BRADEN"],
    "cardio": ["TOOL.HEART", "TOOL.SOFA", "TOOL.NEWS2"],
}

CAREER_PATH_TOOLS: dict[str, list[str]] = {
    "CAREER.GENERALIST": ["TOOL.GCS", "TOOL.BRADEN", "TOOL.MORSE"],
    "CAREER.ICU": ["TOOL.RASS", "TOOL.CAM-ICU", "TOOL.SOFA", "TOOL.APACHE2"],
    "CAREER.EMERGENCY": ["TOOL.NEWS2", "TOOL.MEWS", "TOOL.GCS"],
    "CAREER.MANAGER": ["TOOL.TURNOVER"],
    "CAREER.EDUCATOR": ["TOOL.GCS", "TOOL.BRADEN"],
    "CAREER.RESEARCHER": ["TOOL.GCS", "TOOL.SOFA"],
    "CAREER.STOMA": ["TOOL.BRADEN"],
    "CAREER.ONCOLOGY": ["TOOL.BRADEN", "TOOL.NRS2002"],
    "CAREER.OBSTETRIC": ["TOOL.APGAR", "TOOL.BALLARD"],
    "CAREER.OCCUPATIONAL": ["TOOL.BARTHEL", "TOOL.KATZ"],
}


def filter_valid_tools(codes: list[str], valid: set[str]) -> list[str]:
    return [c for c in codes if c in valid]
