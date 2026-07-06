"""Social image generator — SVG for multiple formats."""
from __future__ import annotations

import html
import re
from pathlib import Path
from uuid import uuid4

from paths import OUT, formats

BRAND = {
    "navy": "#00356B",
    "navy_dark": "#021B4D",
    "teal": "#00C7B1",
    "teal_light": "#00E5D0",
    "white": "#FFFFFF",
    "muted": "#94A3B8",
}


def _esc(t: str) -> str:
    return html.escape(str(t or ""))


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def generate_social_svg(
    *,
    headline: str,
    subheadline: str = "",
    format_id: str = "instagram_post",
    badges: list[str] | None = None,
    cta: str = "",
    persona: str = "",
    country: str = "BR",
) -> dict:
    fmt = formats().get(format_id) or formats().get("instagram_post", {"width": 1080, "height": 1080})
    w, h = int(fmt["width"]), int(fmt["height"])
    is_story = h > w * 1.5
    is_wide = w > h * 1.3

    pad = 48 if w >= 1000 else 24
    title_size = 52 if is_story else (44 if is_wide else 48)
    sub_size = 22 if is_story else 20

    badge_y = h - pad - (80 if is_story else 60)
    badges = badges or ["🩺 Clínico", "📚 Evidências", "🌎 Global"]

    badge_svg = ""
    bx = pad
    for i, b in enumerate(badges[:4]):
        badge_svg += f'''
  <rect x="{bx}" y="{badge_y}" rx="14" ry="14" width="{min(len(b)*9+24, 200)}" height="28" fill="{BRAND['navy_dark']}" opacity="0.85"/>
  <text x="{bx + 12}" y="{badge_y + 19}" fill="{BRAND['teal_light']}" font-family="Segoe UI, Arial, sans-serif" font-size="13">{_esc(b)}</text>'''
        bx += min(len(b) * 9 + 32, 210)

    cta_svg = ""
    if cta:
        cy = h - pad - (120 if is_story else 100)
        cta_svg = f'''
  <rect x="{pad}" y="{cy}" rx="20" ry="20" width="{len(cta)*11+40}" height="40" fill="{BRAND['teal']}"/>
  <text x="{pad + 20}" y="{cy + 26}" fill="{BRAND['white']}" font-family="Segoe UI, Arial, sans-serif" font-size="16" font-weight="600">{_esc(cta)}</text>'''

    meta = f"{persona} · {country}" if persona else country
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{BRAND['navy_dark']}"/>
      <stop offset="100%" style="stop-color:{BRAND['navy']}"/>
    </linearGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <circle cx="{w-80}" cy="{80 if is_story else 100}" r="120" fill="{BRAND['teal']}" opacity="0.12"/>
  <circle cx="{w//2}" cy="{h//2 + (40 if is_story else 0)}" r="{min(w,h)//4}" fill="none" stroke="{BRAND['teal_light']}" stroke-width="2" opacity="0.35"/>
  <rect x="{pad}" y="{pad}" width="4" height="{title_size * 2}" rx="2" fill="{BRAND['teal']}"/>
  <text x="{pad + 20}" y="{pad + title_size}" fill="{BRAND['white']}" font-family="Segoe UI, Arial, sans-serif" font-size="{title_size}" font-weight="700">{_esc(headline[:50])}</text>
  <text x="{pad + 20}" y="{pad + title_size + sub_size + 16}" fill="{BRAND['muted']}" font-family="Segoe UI, Arial, sans-serif" font-size="{sub_size}">{_esc(subheadline[:90])}</text>
  {cta_svg}
  {badge_svg}
  <text x="{pad}" y="{h - pad//2}" fill="{BRAND['muted']}" font-family="Segoe UI, Arial, sans-serif" font-size="12">Calculadoras de Enfermagem · NKOS Studio · {_esc(meta)}</text>
</svg>'''

    OUT.mkdir(parents=True, exist_ok=True)
    file_id = uuid4().hex[:10]
    slug = _slug(headline)
    filename = f"{slug}_{format_id}_{file_id}.svg"
    out_path = OUT / filename
    out_path.write_text(svg, encoding="utf-8")

    return {
        "ok": True,
        "format": format_id,
        "dimensions": {"width": w, "height": h},
        "path": f"assets/images/studio/{filename}",
        "website_path": f"/assets/images/studio/{filename}",
        "absolute_path": str(out_path),
        "filename": filename,
        "svg_preview_chars": len(svg),
    }
