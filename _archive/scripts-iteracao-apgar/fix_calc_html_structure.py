#!/usr/bin/env python3
"""Fix duplicate tool-config and restore correct HTML structure on calculator pages."""
import re
import glob
import os

HTML_DIR = os.path.join(os.path.dirname(__file__), "..", "NIFS", "DELIVERY", "html")

STANDARD_TAIL = """<div id="site-footer"></div>
<div id="site-cookie"></div>

<script src="js/partials-loader.js"></script>
"""


def fix_file(path: str) -> bool:
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if 'id="tool-config"' not in content:
        return False

    original = content

    # Remove duplicate tool-config blocks (keep first only)
    configs = list(re.finditer(
        r'<script type="application/json" id="tool-config">.*?</script>',
        content,
        re.DOTALL,
    ))
    if len(configs) > 1:
        for m in reversed(configs[1:]):
            content = content[: m.start()] + content[m.end() :]

    # Fix about-grid stray closing tag
    content = re.sub(
        r'(</div>\s*)</div>\s*(</section>)',
        r'\1\2',
        content,
        count=1,
    )

    # Extract custom inline scripts (not json, not partials/calc/nurse)
    body_end = content.rfind("</body>")
    if body_end < 0:
        return False

    before_body = content[:body_end]
    custom_scripts = []
    for m in re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>.*?</script>", before_body, re.DOTALL):
        block = m.group(0)
        if 'id="tool-config"' in block:
            continue
        if any(x in block for x in ("partials-loader", "calc-engine", "nurse-palm", "cognitive-ui", "knowledge-graph", "i18n-loader")):
            continue
        custom_scripts.append(block)

    # Rebuild tail: keep everything up to and including </svg></defs></svg> or tool-config+svg
    # Find site-footer marker
    footer_idx = before_body.rfind('<div id="site-footer">')
    if footer_idx < 0:
        return False

    prefix = before_body[:footer_idx].rstrip() + "\n\n"
    new_content = prefix + STANDARD_TAIL
    for script in custom_scripts:
        new_content += "\n" + script + "\n"
    new_content += "</body></html>\n"

    # Preserve anything after </html> accidentally? No.
    if new_content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def main():
    fixed = 0
    for path in sorted(glob.glob(os.path.join(HTML_DIR, "*.html"))):
        if fix_file(path):
            fixed += 1
            print(os.path.basename(path))
    print(f"\nFixed {fixed} files")


if __name__ == "__main__":
    main()
