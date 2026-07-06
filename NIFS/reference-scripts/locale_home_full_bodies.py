"""Full translated body sections for locales without a 2026.1 partition."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

FULL_BODIES: dict[str, dict[str, Any]] = {}


def _hero(
    title: str,
    accent: str,
    subtitle: str,
    img_alt: str,
    cta1: str,
    cta2: str,
    stats: list[tuple[str, str]],
) -> dict[str, Any]:
    return {
        "title": title,
        "title_accent": accent,
        "subtitle": subtitle,
        "image": "homepage-hero.webp",
        "image_alt": img_alt,
        "background": {"color_start": "#002d62", "color_mid": "#0a1628", "color_end": "#334e68"},
        "cta_primary": {"label": cta1, "href": "/ferramentas"},
        "cta_secondary": {"label": cta2, "href": "/sobre"},
        "stats": [{"value": v, "label": l} for v, l in stats],
    }


def _search(label: str, placeholder: str, button: str) -> dict[str, str]:
    return {"label": label, "placeholder": placeholder, "button": button}


def _seo(title: str, description: str) -> dict[str, str]:
    return {"title": title, "description": description}


FULL_BODIES["ro-RO"] = {
    "hero": _hero(
        "Tehnologie și cunoștințe pentru o asistență medicală",
        "mai eficientă și sustenabilă.",
        "Instrumente clinice, protocoale, scări și conținut educațional pentru studenți, asistenți medicali, manageri și instituții de sănătate — cu responsabilitate digitală și impact măsurabil.",
        "Asistent medical într-un mediu clinic",
        "Explorează instrumentele",
        "Despre platformă",
        [("195+", "Țări conectate"), ("Sute de", "Profesioniști impactați"), ("+100", "Instrumente digitale")],
    ),
    "search": _search(
        "De ce ai nevoie astăzi?",
        "Ex.: Picurare, Scala Braden, Insulină, Proces de asistență…",
        "Caută",
    ),
    "seo": _seo(
        "Nursing Calculators | Platformă globală de inteligență clinică",
        "Tehnologie sustenabilă pentru asistența medicală — instrumente, scări, educație și guvernanță. 195+ țări, Nursing Calculators 2026.",
    ),
    "featured": {
        "title": "Cele mai utilizate instrumente",
        "view_all_label": "Vezi toate instrumentele",
        "view_all_href": "/ferramentas",
        "items": [
            {"title": "Calculator picurare", "description": "Calculează picături pe minut în siguranță.", "action_label": "Folosește", "tool_code": "TOOL.INFUSION"},
            {"title": "Scala Braden", "description": "Evaluează riscul de leziuni de presiune.", "action_label": "Aplică", "tool_code": "TOOL.BRADEN"},
            {"title": "Calculator IMC", "description": "Evaluează indicele de masă corporală.", "action_label": "Folosește", "tool_code": "TOOL.BMI"},
            {"title": "Bilanț hidric", "description": "Monitorizează intrările și ieșirile de lichide.", "action_label": "Folosește", "href": "/calculadoras"},
        ],
    },
    "management_block": {
        "title": "Management cu impact",
        "subtitle": "Resurse și indicatori pentru lideri și instituții de sănătate.",
        "links": [
            {"label": "Indicatori și panouri", "href": "/gestao/indicadores", "icon": "chart"},
            {"label": "Managementul protocoalelor", "href": "/protocolos", "icon": "clipboard"},
            {"label": "Calitate și siguranță", "href": "/gestao", "icon": "shield"},
            {"label": "Sustenabilitate", "href": "/sustentabilidade", "icon": "leaf"},
        ],
        "cta": {"label": "Descoperă soluțiile", "href": "/gestao"},
        "dashboard": {
            "title": "Indicatori generali",
            "donut_label": "Rată de aderență",
            "donut_value": "92%",
            "trend_label": "Evenimente adverse",
            "trend_value": "-18%",
        },
    },
    "global_platform": {
        "title": "O platformă globală",
        "description": "Conectăm profesioniști, instituții și cunoștințe în peste 195 de țări, promovând o asistență medicală mai puternică, colaborativă și sustenabilă.",
        "cta": {"label": "Parcursul nostru", "href": "/historia"},
        "stats": [
            {"value": "195+", "label": "Țări conectate", "icon": "globe"},
            {"value": "Sute de", "label": "Profesioniști impactați", "icon": "users"},
            {"value": "Conținut", "label": "În mai multe limbi", "icon": "book"},
        ],
        "community": {
            "title": "Comunitate activă",
            "description": "Împărtășește experiențe și învață de la profesioniști din întreaga lume.",
            "members_label": "+12k",
            "href": "/forum",
            "image": "homepage-section-002.webp",
            "image_alt": "Comunitate globală de asistenți medicali",
            "avatars": ["AM", "JS", "LR", "PF"],
        },
    },
}

FULL_BODIES["el-GR"] = {
    "hero": _hero(
        "Τεχνολογία και γνώση για",
        "πιο αποτελεσματική και βιώσιμη νοσηλευτική.",
        "Κλινικά εργαλεία, πρωτόκολλα, κλίμακες και εκπαιδευτικό περιεχόμενο για φοιτητές, νοσηλευτές, διευθυντές και ιδρύματα υγείας — με ψηφιακή ευθύνη και μετρήσιμο αντίκτυπο.",
        "Νοσηλευτής σε κλινικό περιβάλλον",
        "Εξερεύνηση εργαλείων",
        "Γνωρίστε την πλατφόρμα",
        [("195+", "Συνδεδεμένες χώρες"), ("Εκατοντάδες", "Επηρεαζόμενοι επαγγελματίες"), ("+100", "Ψηφιακά εργαλεία")],
    ),
    "search": _search(
        "Τι χρειάζεστε σήμερα;",
        "Π.χ.: Στάγες, Κλίμακα Braden, Ινσουλίνη, ΔIA…",
        "Αναζήτηση",
    ),
    "seo": _seo(
        "Nursing Calculators | Παγκόσμια πλατφόρμα κλινικής νοημοσύνης",
        "Βιώσιμη τεχνολογία για τη νοσηλευτική — εργαλεία, κλίμακες, εκπαίδευση και διακυβέρνηση. 195+ χώρες, Nursing Calculators 2026.",
    ),
    "featured": {
        "title": "Τα πιο χρησιμοποιούμενα εργαλεία",
        "view_all_label": "Δείτε όλα τα εργαλεία",
        "view_all_href": "/ferramentas",
        "items": [
            {"title": "Υπολογιστής στάγων", "description": "Υπολογίστε στάγες ανά λεπτό με ασφάλεια.", "action_label": "Χρήση", "tool_code": "TOOL.INFUSION"},
            {"title": "Κλίμακα Braden", "description": "Αξιολογήστε τον κίνδυνο κατακλίσεων.", "action_label": "Εφαρμογή", "tool_code": "TOOL.BRADEN"},
            {"title": "Υπολογιστής ΔΜΣ", "description": "Αξιολογήστε τον δείκτη μάζας σώματος.", "action_label": "Χρήση", "tool_code": "TOOL.BMI"},
            {"title": "Υδατικό ισοζύγιο", "description": "Παρακολουθήστε εισροές και εκροές υγρών.", "action_label": "Χρήση", "href": "/calculadoras"},
        ],
    },
    "management_block": {
        "title": "Διοίκηση με αντίκτυπο",
        "subtitle": "Πόροι και δείκτες για ηγέτες και ιδρύματα υγείας.",
        "links": [
            {"label": "Δείκτες και πίνακες", "href": "/gestao/indicadores", "icon": "chart"},
            {"label": "Διαχείριση πρωτοκόλλων", "href": "/protocolos", "icon": "clipboard"},
            {"label": "Ποιότητα και ασφάλεια", "href": "/gestao", "icon": "shield"},
            {"label": "Βιωσιμότητα", "href": "/sustentabilidade", "icon": "leaf"},
        ],
        "cta": {"label": "Ανακαλύψτε λύσεις", "href": "/gestao"},
        "dashboard": {
            "title": "Γενικοί δείκτες",
            "donut_label": "Ποσοστό συμμόρφωσης",
            "donut_value": "92%",
            "trend_label": "Δυσμενή συμβάντα",
            "trend_value": "-18%",
        },
    },
    "global_platform": {
        "title": "Μια παγκόσμια πλατφόρμα",
        "description": "Συνδέουμε επαγγελματίες, ιδρύματα και γνώση σε περισσότερες από 195 χώρες, προωθώντας ισχυρότερη, συνεργατική και βιώσιμη νοσηλευτική.",
        "cta": {"label": "Το ταξίδι μας", "href": "/historia"},
        "stats": [
            {"value": "195+", "label": "Συνδεδεμένες χώρες", "icon": "globe"},
            {"value": "Εκατοντάδες", "label": "Επηρεαζόμενοι επαγγελματίες", "icon": "users"},
            {"value": "Περιεχόμενο", "label": "Σε πολλές γλώσσες", "icon": "book"},
        ],
        "community": {
            "title": "Ενεργή κοινότητα",
            "description": "Μοιραστείτε εμπειρίες και μάθετε από επαγγελματίες σε όλο τον κόσμο.",
            "members_label": "+12k",
            "href": "/forum",
            "image": "homepage-section-002.webp",
            "image_alt": "Παγκόσμια κοινότητα νοσηλευτών",
            "avatars": ["AM", "JS", "LR", "PF"],
        },
    },
}


def get_full_body(locale: str) -> dict[str, Any]:
    return deepcopy(FULL_BODIES.get(locale, {}))
