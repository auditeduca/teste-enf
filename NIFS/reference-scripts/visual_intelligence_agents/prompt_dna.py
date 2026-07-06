"""Nursing Visual DNA — structured prompt builder for image generation."""
from __future__ import annotations

from typing import Any

from paths import brand_identity, cultural_rules, og_templates, visual_personas


def build_visual_dna(
    *,
    locale: str = "pt-BR",
    persona: str = "profissional",
    tool: str | None = None,
    page: str | None = None,
    mode: str = "study",
    theme: str = "light",
) -> dict[str, Any]:
    country = locale.split("-")[-1].upper() if "-" in locale else "BR"
    if country == "BR" or len(country) > 2:
        country = {"pt": "BR", "en": "US", "ja": "JP", "zh": "CN", "de": "DE", "fr": "FR", "ar": "SA"}.get(
            locale.split("-")[0], "BR"
        )

    persona_data = visual_personas().get("personas", {}).get(persona, {})
    cultural = cultural_rules().get("countries", {}).get(country, {})
    brand = brand_identity()

    tpl_key = page or tool or "home"
    tpl = og_templates().get("templates", {}).get(tpl_key, {})

    return {
        "locale": locale,
        "country": country,
        "persona": persona,
        "tool": tool,
        "page": page,
        "mode": mode,
        "theme": theme,
        "archetype": tpl.get("archetype", persona_data.get("visual_language", "clinical")),
        "specialty": tpl.get("specialty"),
        "brand_colors": brand.get("colors", {}),
        "cultural_preferences": cultural,
        "persona_preferences": persona_data,
        "template": {
            "title": tpl.get("title"),
            "subtitle": tpl.get("subtitle"),
            "hero_visual": tpl.get("hero_visual"),
        },
    }


def build_prompt(dna: dict[str, Any], *, asset_type: str = "og") -> str:
    brand = brand_identity()
    colors = brand.get("colors", {})
    cultural = dna.get("cultural_preferences", {})
    persona = dna.get("persona_preferences", {})
    tpl = dna.get("template", {})

    parts = [
        f"Professional nursing visual for {asset_type} asset.",
        f"Locale: {dna.get('locale')} ({dna.get('country')}).",
        f"Persona: {dna.get('persona')} — {persona.get('objective', 'clinical practice')}.",
        f"Environment: {persona.get('environment', 'clinical')}.",
        f"Archetype: {dna.get('archetype')}.",
        f"Title context: {tpl.get('title', 'Calculadoras de Enfermagem')}.",
        f"Hero elements: {tpl.get('hero_visual', 'nurse with tablet')}.",
        f"Brand colors: primary {colors.get('primary')}, secondary {colors.get('secondary')}, accent {colors.get('accent')}.",
        f"Cultural style: smile {cultural.get('smile_level', 'medium')}, posture {cultural.get('body_language', 'professional')}, background {cultural.get('background_style', 'clinical')}.",
        "Composition: 60% text left, 40% hero right, max 4 footer badges.",
        "Open Graph optimized: 1200x630, no buttons, no cards, no navigation.",
        "Expression: 70% confidence, 20% empathy, 10% smile.",
        "Angle: 3/4 frontal, gaze toward professional activity not camera.",
        "Avoid: stock photo smile, fashion poses, incorrect stethoscope, futuristic excess.",
    ]
    if dna.get("mode") == "emergency":
        parts.append("Mode emergency: high contrast, minimal distraction, functional.")
    if asset_type == "og":
        parts.append("Must be readable at 150px thumbnail width.")
    return " ".join(parts)
