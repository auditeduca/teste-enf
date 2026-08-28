#!/usr/bin/env python3
"""Remove CIP/disclaimer sections and standardize footer scripts on calculator pages."""
import re
import glob
import os

HTML_DIR = os.path.join(os.path.dirname(__file__), "..", "NIFS", "DELIVERY", "html")

DISCLAIMER_RE = re.compile(
    r'\s*<div class="disclaimer-card">.*?</div>\s*',
    re.DOTALL,
)

CIP_SECTION_RE = re.compile(
    r'\s*<!--[^\n]*Clinical Intelligence Package[^\n]*-->\s*'
    r'<section class="cip-section">.*?</section>\s*',
    re.DOTALL,
)

COG_SECTION_RE = re.compile(
    r'\s*<!--[^\n]*Nurse-PaLM Cognitive[^\n]*-->\s*'
    r'<section class="cog-section-wrapper">.*?</section>\s*',
    re.DOTALL,
)

KG_LINKS_RE = re.compile(
    r'\s*<!--[^\n]*Knowledge Graph[^\n]*-->\s*'
    r'<section class="cip-kg-links">.*?</section>\s*',
    re.DOTALL,
)

# Fallback patterns without comments
CIP_FALLBACK = re.compile(r'\s*<section class="cip-section">.*?</section>\s*', re.DOTALL)
COG_FALLBACK = re.compile(r'\s*<section class="cog-section-wrapper">.*?</section>\s*', re.DOTALL)
KG_FALLBACK = re.compile(r'\s*<section class="cip-kg-links">.*?</section>\s*', re.DOTALL)

FOOTER_SCRIPTS_RE = re.compile(
    r'(<div id="site-cookie"></div>\s*)'
    r'(?:<script[^>]*>.*?</script>\s*|<script[^>]*/>\s*)+'
    r'(</body>)',
    re.DOTALL,
)

STANDARD_FOOTER = '<div id="site-cookie"></div>\n\n<script src="js/partials-loader.js"></script>\n'


def cleanup_file(path: str) -> list[str]:
    changes = []
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if 'id="tool-config"' not in content:
        return changes

    original = content

    if DISCLAIMER_RE.search(content):
        content = DISCLAIMER_RE.sub("\n", content)
        changes.append("disclaimer")

    for pattern, name in [
        (CIP_SECTION_RE, "cip"),
        (CIP_FALLBACK, "cip"),
        (COG_SECTION_RE, "cog"),
        (COG_FALLBACK, "cog"),
        (KG_LINKS_RE, "kg"),
        (KG_FALLBACK, "kg"),
    ]:
        if pattern.search(content):
            content = pattern.sub("\n", content)
            if name not in changes:
                changes.append(name)

    # Fix about-grid to single column when disclaimer removed
    if "disclaimer" in changes:
        content = content.replace(
            'class="about-grid"',
            'class="about-grid about-grid--single"',
            1,
        )

    # Standardize footer: keep custom inline scripts (e.g. apgar) but remove duplicate loaders
    if '<div id="site-cookie"></div>' in content:
        # Remove duplicate script tags before </body> except inline scripts and partials-loader
        body_end = content.rfind("</body>")
        if body_end > 0:
            before_body = content[:body_end]
            after_body = content[body_end:]

            # Extract inline scripts to preserve (apgar custom logic etc.)
            inline_scripts = re.findall(
                r'<script(?![^>]*\bsrc=)[^>]*>.*?</script>',
                before_body,
                re.DOTALL,
            )

            # Find site-cookie div position
            cookie_idx = before_body.rfind('<div id="site-cookie"></div>')
            if cookie_idx >= 0:
                prefix = before_body[: cookie_idx + len('<div id="site-cookie"></div>')]
                new_tail = "\n\n<script src=\"js/partials-loader.js\"></script>\n"
                for script in inline_scripts:
                    if "partials-loader" not in script and "calc-engine" not in script:
                        if "nurse-palm" not in script and "cognitive-ui" not in script:
                            if "knowledge-graph" not in script and "i18n-loader" not in script:
                                new_tail += "\n" + script + "\n"
                content = prefix + new_tail + after_body
                changes.append("footer")

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    return changes


def main():
    files = sorted(glob.glob(os.path.join(HTML_DIR, "*.html")))
    total = 0
    for path in files:
        changes = cleanup_file(path)
        if changes:
            total += 1
            print(f"{os.path.basename(path)}: {', '.join(changes)}")
    print(f"\nUpdated {total} files")


if __name__ == "__main__":
    main()
