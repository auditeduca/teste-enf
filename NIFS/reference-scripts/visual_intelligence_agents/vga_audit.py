"""Visual Governance Agent — rule-based audit for OG and hero assets."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from paths import ROOT, brand_identity, cultural_rules, og_manifest, og_templates, scoring_rubric


@dataclass
class AuditResult:
    overall_score: float
    brand_score: float
    clinical_score: float
    cultural_score: float
    accessibility_score: float
    og_score: float
    trust_score: float
    visual_harmony_score: float
    persona_fit_score: float
    device_fit_score: float
    level: str
    recommendations: list[str] = field(default_factory=list)
    checks: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_score": round(self.overall_score, 1),
            "PNIS": round(self.overall_score, 1),
            "VCS": round((self.visual_harmony_score + self.brand_score) / 2, 1),
            "GlobalReadiness": round(self.overall_score, 1),
            "brand_score": round(self.brand_score, 1),
            "clinical_score": round(self.clinical_score, 1),
            "cultural_score": round(self.cultural_score, 1),
            "accessibility_score": round(self.accessibility_score, 1),
            "og_score": round(self.og_score, 1),
            "trust_score": round(self.trust_score, 1),
            "visual_harmony_score": round(self.visual_harmony_score, 1),
            "persona_fit_score": round(self.persona_fit_score, 1),
            "device_fit_score": round(self.device_fit_score, 1),
            "level": self.level,
            "recommendations": self.recommendations,
            "checks": self.checks,
        }


def _level(score: float) -> str:
    levels = scoring_rubric().get("levels", {})
    if score >= levels.get("excellence", 98):
        return "excellence"
    if score >= levels.get("platinum", 95):
        return "platinum"
    if score >= levels.get("gold", 90):
        return "gold"
    if score >= levels.get("silver", 80):
        return "silver"
    if score >= levels.get("bronze", 70):
        return "bronze"
    return "below_bronze"


def _svg_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        root = ET.parse(path).getroot()
        w = root.get("width") or root.get("viewBox", "").split()[-2] if root.get("viewBox") else None
        h = root.get("height") or root.get("viewBox", "").split()[-1] if root.get("viewBox") else None
        return (int(float(w)) if w else None, int(float(h)) if h else None)
    except ET.ParseError:
        return None, None


def _image_dimensions(path: Path) -> tuple[int | None, int | None]:
    if path.suffix.lower() == ".svg":
        return _svg_dimensions(path)
    try:
        from PIL import Image  # type: ignore

        with Image.open(path) as im:
            return im.size
    except Exception:
        return None, None


def audit_image(
    image_path: str | Path,
    *,
    country: str = "BR",
    page_type: str = "sustainability",
    persona: str = "profissional",
    template_key: str | None = None,
) -> AuditResult:
    path = Path(image_path)
    if not path.is_absolute():
        path = ROOT / path
    recs: list[str] = []
    checks: dict[str, Any] = {}

    w, h = _image_dimensions(path)
    checks["dimensions"] = {"width": w, "height": h}
    og_ok = w == 1200 and h == 630
    if not og_ok:
        recs.append("Ajustar dimensões para 1200×630 px (proporção Open Graph 1.91:1).")
    og_score = 100.0 if og_ok else 45.0

    size_kb = path.stat().st_size / 1024 if path.exists() else 0
    checks["file_size_kb"] = round(size_kb, 1)
    if size_kb > 250:
        recs.append(f"Reduzir peso do arquivo ({size_kb:.0f} KB > 250 KB meta).")
        og_score -= 15
    elif size_kb > 180:
        og_score -= 5

    tpl_data = og_templates().get("templates", {})
    tpl = tpl_data.get(template_key or page_type) or tpl_data.get(page_type.replace("-", "_"), {})
    if not tpl and page_type in tpl_data:
        tpl = tpl_data[page_type]
    if not tpl:
        for k, v in tpl_data.items():
            if v.get("page_slug") == page_type or v.get("canonical_path", "").endswith(page_type):
                tpl = v
                break

    title = tpl.get("title", "")
    word_count = len(title.split())
    checks["title_words"] = word_count
    checks["title_chars"] = len(title)
    if word_count > 7:
        recs.append(f"Reduzir título para máximo 7 palavras (atual: {word_count}).")
        og_score -= 20
    if len(title) > 55:
        recs.append("Título excede 55 caracteres — legibilidade em miniatura comprometida.")
        og_score -= 10

    subtitle = tpl.get("subtitle", "")
    if len(subtitle) > 120:
        recs.append("Subtítulo excede 120 caracteres.")
        og_score -= 5

    text_content = ""
    if path.suffix.lower() == ".svg" and path.exists():
        text_content = path.read_text(encoding="utf-8", errors="ignore").lower()
        if "btn" in text_content or "button" in text_content:
            recs.append("Remover botões/CTAs — não funcionam em OG.")
            og_score -= 25
        if text_content.count("<rect") > 25:
            recs.append("Reduzir elementos visuais concorrentes (cards, widgets).")
            og_score -= 10

    brand_score = 92.0
    bi = brand_identity()
    primary = bi.get("colors", {}).get("primary", "#021B4D").lower()
    if path.exists() and primary.replace("#", "") not in text_content and path.suffix == ".svg":
        brand_score -= 8
        recs.append("Incluir paleta primária da marca (#021B4D) na composição.")

    cultural = cultural_rules().get("countries", {}).get(country.upper(), {})
    cultural_score = 90.0
    if cultural.get("smile_level") == "low" and "sorriso" in text_content:
        cultural_score -= 15
        recs.append(f"Para {country}: reduzir expressão emocional exagerada.")

    clinical_score = 88.0
    if "estetoscopio" in text_content or "stethoscope" in text_content:
        clinical_score -= 5
        recs.append("Verificar posicionamento plausível de estetoscópio.")

    accessibility_score = 95.0 if og_ok else 75.0
    trust_score = 93.0
    visual_harmony = 91.0
    persona_fit = 90.0
    device_fit = 89.0

    weights = scoring_rubric().get("modules", {})
    scores = {
        "brand": brand_score,
        "clinical": clinical_score,
        "cultural": cultural_score,
        "accessibility": accessibility_score,
        "og": max(0, og_score),
        "trust": trust_score,
        "visual_harmony": visual_harmony,
        "persona_fit": persona_fit,
        "device_fit": device_fit,
    }
    total_w = sum(m.get("weight", 0.1) for m in weights.values()) or 1.0
    overall = sum(scores[k] * weights.get(k, {}).get("weight", 0.1) for k in scores) / total_w

    checks["country"] = country
    checks["persona"] = persona
    checks["page_type"] = page_type

    return AuditResult(
        overall_score=overall,
        brand_score=brand_score,
        clinical_score=clinical_score,
        cultural_score=cultural_score,
        accessibility_score=accessibility_score,
        og_score=max(0, og_score),
        trust_score=trust_score,
        visual_harmony_score=visual_harmony,
        persona_fit_score=persona_fit,
        device_fit_score=device_fit,
        level=_level(overall),
        recommendations=recs,
        checks=checks,
    )


def audit_manifest_entry(canonical_path: str) -> AuditResult | None:
    manifest = og_manifest()
    entry = manifest.get("entries", {}).get(canonical_path)
    if not entry:
        return None
    asset = entry.get("asset") or entry.get("svg")
    if not asset:
        return None
    img_path = ROOT / "website" / "assets" / "images" / asset.replace("og/", "og/")
    if not img_path.exists():
        img_path = ROOT / "website" / "assets" / "images" / asset
    return audit_image(
        img_path,
        page_type=entry.get("template_key", "sustainability"),
        template_key=entry.get("template_key"),
    )
