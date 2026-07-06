"""Open Graph image generator — 1200×630 SVG (+ optional PNG via Pillow)."""
from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from paths import OG_OUT, OG_RETINA, brand_identity, og_templates, save_og_manifest

W, H = 1200, 630
SAFE = 60
TEXT_COL = 720  # 60% of 1200


def _esc(text: str) -> str:
    return html.escape(str(text or ""))


def _wrap_title(title: str, max_chars: int = 28) -> list[str]:
    words = title.split()
    lines: list[str] = []
    current: list[str] = []
    length = 0
    for w in words:
        add = len(w) + (1 if current else 0)
        if length + add > max_chars and current:
            lines.append(" ".join(current))
            current = [w]
            length = len(w)
        else:
            current.append(w)
            length += add
    if current:
        lines.append(" ".join(current))
    return lines[:3]


def _hero_visual_svg(hero_key: str, x0: int) -> str:
    """Abstract hero composition — no stock photo dependency."""
    cx = x0 + (W - x0) // 2
    cy = H // 2 - 20
    globe = f"""
  <circle cx="{cx}" cy="{cy}" r="110" fill="none" stroke="#00E5D0" stroke-width="2" opacity="0.6"/>
  <ellipse cx="{cx}" cy="{cy}" rx="110" ry="40" fill="none" stroke="#00C7B1" stroke-width="1.5" opacity="0.5"/>
  <ellipse cx="{cx}" cy="{cy}" rx="40" ry="110" fill="none" stroke="#00C7B1" stroke-width="1.5" opacity="0.5"/>
  <circle cx="{cx - 30}" cy="{cy - 20}" r="6" fill="#00E5D0" opacity="0.8"/>
  <circle cx="{cx + 40}" cy="{cy + 10}" r="4" fill="#00C7B1" opacity="0.7"/>
"""
    nurse = f"""
  <rect x="{cx - 55}" y="{cy - 80}" width="110" height="140" rx="24" fill="#00356B" opacity="0.85"/>
  <circle cx="{cx}" cy="{cy - 95}" r="28" fill="#00C7B1" opacity="0.35"/>
  <rect x="{cx - 35}" y="{cy - 30}" width="70" height="45" rx="8" fill="#021B4D" stroke="#00E5D0" stroke-width="1.5"/>
  <rect x="{cx - 25}" y="{cy - 22}" width="50" height="28" rx="4" fill="#001A3A" opacity="0.9"/>
"""
    leaves = """
  <path d="M950 520 Q970 480 990 520 Q970 540 950 520" fill="#00C7B1" opacity="0.5"/>
  <path d="M1010 500 Q1030 460 1050 500 Q1030 520 1010 500" fill="#00E5D0" opacity="0.4"/>
  <path d="M1070 530 Q1090 490 1110 530 Q1090 550 1070 530" fill="#00C7B1" opacity="0.35"/>
"""
    shield = f"""
  <path d="M{cx} {cy - 90} L{cx + 70} {cy - 50} L{cx + 70} {cy + 20} Q{cx + 70} {cy + 80} {cx} {cy + 110} Q{cx - 70} {cy + 80} {cx - 70} {cy + 20} L{cx - 70} {cy - 50} Z"
        fill="none" stroke="#00E5D0" stroke-width="3" opacity="0.7"/>
  <path d="M{cx - 25} {cy + 5} L{cx - 5} {cy + 30} L{cx + 35} {cy - 20}" fill="none" stroke="#00C7B1" stroke-width="4" stroke-linecap="round"/>
"""
    if "shield" in hero_key:
        return shield + leaves
    if "globe" in hero_key or "sustain" in hero_key:
        return globe + nurse + leaves
    if "study" in hero_key or "library" in hero_key or "education" in hero_key:
        return nurse + f'<rect x="{cx - 80}" y="{cy + 40}" width="160" height="8" rx="4" fill="#00C7B1" opacity="0.4"/>'
    if "dashboard" in hero_key or "calculator" in hero_key or "scale" in hero_key:
        bars = ""
        for i, h in enumerate([40, 65, 50, 80, 55]):
            bars += f'<rect x="{cx - 60 + i * 28}" y="{cy + 40 - h}" width="18" height="{h}" rx="4" fill="#00C7B1" opacity="{0.3 + i * 0.1}"/>'
        return nurse + bars + globe
    if "neuro" in hero_key or "glasgow" in hero_key:
        return nurse + f'<circle cx="{cx + 60}" cy="{cy - 60}" r="20" fill="#FF3B30" opacity="0.25"/>'
    return globe + nurse


def build_og_svg(
    *,
    title: str,
    subtitle: str,
    badges: list[str],
    brand: str = "Calculadoras de Enfermagem",
    tagline: str = "Global Platform",
    hero_visual: str = "nurse_tablet_globe",
) -> str:
    bi = brand_identity()
    colors = bi.get("colors", {})
    primary = colors.get("primary", "#021B4D")
    secondary = colors.get("secondary", "#00C7B1")
    accent = colors.get("accent", "#00E5D0")

    title_lines = _wrap_title(title)
    title_y = 200
    title_svg = ""
    for i, line in enumerate(title_lines):
        title_svg += f'<tspan x="{SAFE}" dy="{"0" if i == 0 else "68"}">{_esc(line)}</tspan>'

    badge_y = H - SAFE - 10
    badge_x = SAFE
    badges_svg = ""
    for badge in badges[:4]:
        badges_svg += f"""
  <text x="{badge_x}" y="{badge_y}" font-family="system-ui,sans-serif" font-size="22" fill="#FFFFFF" opacity="0.92">{_esc(badge)}</text>"""
        badge_x += 280

    hero = _hero_visual_svg(hero_visual, TEXT_COL)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{_esc(title)}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{primary}"/>
      <stop offset="40%" stop-color="#00356B"/>
      <stop offset="100%" stop-color="#001A3A"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect x="0" y="0" width="{TEXT_COL}" height="{H}" fill="{primary}" opacity="0.15"/>
  <line x1="{TEXT_COL}" y1="{SAFE}" x2="{TEXT_COL}" y2="{H - SAFE}" stroke="{secondary}" stroke-width="1" opacity="0.25"/>
  <!-- Header / logo area -->
  <text x="{SAFE}" y="{SAFE + 36}" font-family="system-ui,sans-serif" font-size="26" font-weight="700" fill="{accent}">{_esc(brand)}</text>
  <text x="{SAFE}" y="{SAFE + 64}" font-family="system-ui,sans-serif" font-size="16" fill="#FFFFFF" opacity="0.65">{_esc(tagline)}</text>
  <!-- Title -->
  <text x="{SAFE}" y="{title_y}" font-family="system-ui,sans-serif" font-size="52" font-weight="800" fill="#FFFFFF" line-height="1.05">{title_svg}</text>
  <!-- Subtitle -->
  <text x="{SAFE}" y="{title_y + 68 * len(title_lines) + 24}" font-family="system-ui,sans-serif" font-size="24" fill="#FFFFFF" opacity="0.82">{_esc(subtitle[:120])}</text>
  <!-- Hero visual (right 40%) -->
  {hero}
  <!-- Footer badges -->
  <line x1="{SAFE}" y1="{H - SAFE - 36}" x2="{W - SAFE}" y2="{H - SAFE - 36}" stroke="{secondary}" stroke-width="1" opacity="0.2"/>
  {badges_svg}
</svg>
"""


def _resolve_template(template_key: str, locale: str = "pt-BR") -> dict[str, Any]:
    data = og_templates()
    tpl = data.get("templates", {}).get(template_key)
    if not tpl:
        raise KeyError(f"Unknown OG template: {template_key}")
    out = dict(tpl)
    lang = locale.split("-")[0] if locale else "pt"
    overrides = (tpl.get("locale_overrides") or {}).get(lang, {})
    out.update(overrides)
    return out


def generate_og(
    template_key: str,
    *,
    locale: str = "pt-BR",
    persona: str | None = None,
    output_name: str | None = None,
) -> dict[str, Any]:
    tpl = _resolve_template(template_key, locale)
    filename = output_name or f"{template_key}-{locale.lower()}.svg"
    OG_OUT.mkdir(parents=True, exist_ok=True)
    out_path = OG_OUT / filename

    svg = build_og_svg(
        title=tpl["title"],
        subtitle=tpl["subtitle"],
        badges=tpl.get("badges", []),
        hero_visual=tpl.get("hero_visual", "nurse_clinical"),
    )
    out_path.write_text(svg, encoding="utf-8", newline="\n")

    png_path: Path | None = None
    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore

        png_name = filename.replace(".svg", ".jpg")
        png_path = OG_OUT / png_name
        img = Image.new("RGB", (W, H), "#021B4D")
        draw = ImageDraw.Draw(img)
        for y in range(H):
            r = int(2 + (y / H) * 1)
            g = int(27 + (y / H) * 40)
            b = int(77 + (y / H) * 30)
            draw.line([(0, y), (W, y)], fill=(r, g, b))
        try:
            font_title = ImageFont.truetype("arial.ttf", 48)
            font_sub = ImageFont.truetype("arial.ttf", 22)
            font_sm = ImageFont.truetype("arial.ttf", 18)
        except OSError:
            font_title = ImageFont.load_default()
            font_sub = font_title
            font_sm = font_title
        draw.text((SAFE, SAFE + 10), "Calculadoras de Enfermagem", fill="#00E5D0", font=font_sm)
        y_t = 180
        for line in _wrap_title(tpl["title"], 22):
            draw.text((SAFE, y_t), line, fill="#FFFFFF", font=font_title)
            y_t += 56
        draw.text((SAFE, y_t + 10), tpl["subtitle"][:120], fill="#CCCCCC", font=font_sub)
        badge_y = H - SAFE - 8
        bx = SAFE
        for badge in tpl.get("badges", [])[:4]:
            draw.text((bx, badge_y), badge, fill="#FFFFFF", font=font_sm)
            bx += 260
        img.save(png_path, "JPEG", quality=85, optimize=True)
    except ImportError:
        png_path = None

    rel_svg = f"og/{filename}"
    rel_png = f"og/{filename.replace('.svg', '.jpg')}" if png_path and png_path.exists() else rel_svg
    asset_path = rel_png if png_path and png_path.exists() else rel_svg

    entry = {
        "template_key": template_key,
        "locale": locale,
        "persona": persona,
        "title": tpl["title"],
        "subtitle": tpl["subtitle"],
        "canonical_path": tpl.get("canonical_path"),
        "svg": rel_svg,
        "jpg": rel_png if png_path and png_path.exists() else None,
        "asset": asset_path,
        "width": W,
        "height": H,
    }

    manifest = {"schema_version": "2026.3.0", "entries": {}}
    from paths import og_manifest

    manifest = og_manifest()
    manifest.setdefault("entries", {})
    path_key = tpl.get("canonical_path", f"/{template_key}")
    manifest["entries"][path_key] = entry
    save_og_manifest(manifest)

    return {"ok": True, "path": str(out_path), "asset": asset_path, "entry": entry}


def generate_all(*, locale: str = "pt-BR") -> dict[str, Any]:
    data = og_templates()
    results = []
    errors = []
    for key in data.get("templates", {}):
        try:
            results.append(generate_og(key, locale=locale))
        except Exception as exc:
            errors.append({"template": key, "error": str(exc)})
    return {"ok": not errors, "generated": len(results), "errors": errors, "results": results}
