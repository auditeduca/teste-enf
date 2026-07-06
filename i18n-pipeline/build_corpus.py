#!/usr/bin/env python3
"""Consolida o conteúdo único de todas as páginas (extracted/pages/*.json)
num corpus global deduplicado em português: extracted/corpus_pt.json.

Formato: {"strings": {texto_pt: {"count": n, "pages": [até 8 páginas]}},
          "stats": {...}}

O corpus é a fonte da tradução em lote (translate_clinical.py --all) e do
dicionário global por idioma (translations/{lang}/_global.json): cada string
é traduzida UMA vez e reaproveitada em todas as páginas onde ocorre.
"""

import json
from collections import OrderedDict
from pathlib import Path

from translate_clinical import collect_strings

PIPELINE = Path(__file__).resolve().parent
PAGES = PIPELINE / "extracted" / "pages"
OUT = PIPELINE / "extracted" / "corpus_pt.json"


def page_strings(data: dict, stem: str) -> list[str]:
    strings = collect_strings(data.get("tool_config")) if data.get("tool_config") else []
    strings += [v for v in (data.get("seo") or {}).values() if isinstance(v, str) and v.strip()]
    strings += [t for _, t in (data.get("unique_texts") or []) if t and t.strip()]
    deep = PIPELINE / "extracted" / "pages_deep" / f"{stem}.json"
    if deep.is_file():
        dd = json.loads(deep.read_text(encoding="utf-8"))
        strings += (dd.get("texts") or []) + (dd.get("attrs") or [])
    return list(dict.fromkeys(strings))


def main() -> None:
    corpus: OrderedDict[str, dict] = OrderedDict()
    n_pages = 0
    for f in sorted(PAGES.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        n_pages += 1
        for s in page_strings(data, f.stem):
            e = corpus.setdefault(s, {"count": 0, "pages": []})
            e["count"] += 1
            if len(e["pages"]) < 8:
                e["pages"].append(f.stem)
    total = sum(e["count"] for e in corpus.values())
    stats = {
        "pages": n_pages,
        "occurrences": total,
        "unique_strings": len(corpus),
        "shared_2plus": sum(1 for e in corpus.values() if e["count"] >= 2),
        "chars": sum(len(s) for s in corpus),
    }
    OUT.write_text(json.dumps({"stats": stats, "strings": corpus},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(stats, indent=2))
    print(f"corpus salvo em {OUT.relative_to(PIPELINE)}")


if __name__ == "__main__":
    main()
