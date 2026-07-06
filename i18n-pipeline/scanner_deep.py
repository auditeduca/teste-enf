#!/usr/bin/env python3
"""Scanner profundo — extrai TODOS os nós de texto visíveis do corpo das
páginas pt-BR, cobrindo o que a Fase 1 não capturou (prosa de artigos e
calculadoras de formato antigo, sem tool-config).

Saída: extracted/pages_deep/{page}.json  -> {"texts": [...], "attrs": [...]}

- "texts": conteúdo de nós de texto (entre tags), exatamente como no fonte.
- "attrs": valores de atributos visíveis (alt, title, placeholder, aria-label).

O translate_clinical.py usa esses textos com substituição DELIMITADA
(">texto<" / '"texto"') para evitar colisão de substrings curtas.

Uso: python scanner_deep.py [pagina.html ...]   (sem args = todas as 205)
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent
SITE = PIPELINE.parent / "reference-website"
OUT = PIPELINE / "extracted" / "pages_deep"

SKIP_TAGS = {"script", "style", "noscript", "svg", "code", "pre", "template"}
VISIBLE_ATTRS = {"alt", "title", "placeholder", "aria-label"}
HAS_LETTER = re.compile(r"[A-Za-zÀ-ÿ]")


class TextCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.texts: list[str] = []
        self.attrs: list[str] = []
        self._skip_depth = 0
        self._in_body = False

    META_KEYS = {"keywords", "description", "og:title", "og:description",
                 "twitter:title", "twitter:description"}

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self._in_body = True
        if tag in SKIP_TAGS:
            self._skip_depth += 1
        d = dict(attrs)
        if tag == "meta" and (d.get("name") or d.get("property")) in self.META_KEYS:
            v = d.get("content")
            if v and len(v.strip()) >= 4 and HAS_LETTER.search(v):
                self.attrs.append(v)
        for k, v in attrs:
            if k in VISIBLE_ATTRS and v and len(v.strip()) >= 4 and HAS_LETTER.search(v):
                self.attrs.append(v)

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data):
        if not self._in_body or self._skip_depth:
            return
        s = data.strip()
        if len(s) >= 4 and HAS_LETTER.search(s):
            self.texts.append(s)


def scan(page: str) -> dict:
    html = (SITE / page).read_text(encoding="utf-8")
    p = TextCollector()
    p.feed(html)
    return {
        "texts": list(dict.fromkeys(p.texts)),
        "attrs": list(dict.fromkeys(p.attrs)),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if len(sys.argv) > 1:
        pages = [p if p.endswith(".html") else p + ".html" for p in sys.argv[1:]]
    else:
        pages = sorted(f.stem + ".html" for f in (PIPELINE / "extracted" / "pages").glob("*.json"))
    total_t = total_a = 0
    for page in pages:
        if not (SITE / page).is_file():
            print(f"[{page}] não existe — pulado")
            continue
        d = scan(page)
        (OUT / (Path(page).stem + ".json")).write_text(
            json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        total_t += len(d["texts"])
        total_a += len(d["attrs"])
    print(f"{len(pages)} páginas -> {total_t} nós de texto, {total_a} atributos "
          f"(antes de dedupe global)")


if __name__ == "__main__":
    main()
