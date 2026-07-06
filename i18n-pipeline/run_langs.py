#!/usr/bin/env python3
"""Orquestrador da Fase 3 — roda translate_clinical.py --all para vários
idiomas, N em paralelo, com log e QA automático por idioma.

Uso:
  python run_langs.py --langs fr de it            # idiomas específicos
  python run_langs.py --rest                      # todos os que faltam
  python run_langs.py --rest --parallel 2         # (padrão 2)

Log por idioma em logs/translate_{lang}.log; resumo de QA no final.
Retomável: dicionários globais já existentes são reaproveitados.
"""

import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent
LOGS = PIPELINE / "logs"

from translate_clinical import LANG_NAMES  # noqa: E402


def run_lang(lang: str) -> tuple[str, int, str]:
    LOGS.mkdir(exist_ok=True)
    log = LOGS / f"translate_{lang}.log"
    with log.open("a", encoding="utf-8") as fh:
        p = subprocess.run(
            [sys.executable, "-u", str(PIPELINE / "translate_clinical.py"),
             "--lang", lang, "--all"],
            stdout=fh, stderr=subprocess.STDOUT, cwd=PIPELINE,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    with log.open("a", encoding="utf-8") as fh:
        subprocess.run(
            [sys.executable, "-u", str(PIPELINE / "verify_agent.py"),
             "--lang", lang, "--all"],
            stdout=fh, stderr=subprocess.STDOUT, cwd=PIPELINE,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    qa = subprocess.run(
        [sys.executable, str(PIPELINE / "qa_check.py"), "--lang", lang],
        capture_output=True, text=True, cwd=PIPELINE,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    tail = "\n".join((qa.stdout or "").strip().splitlines()[-13:])
    return lang, p.returncode, tail


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", nargs="*", default=[])
    ap.add_argument("--rest", action="store_true",
                    help="todos os idiomas sem dicionário global completo")
    ap.add_argument("--parallel", type=int, default=2)
    args = ap.parse_args()

    langs = args.langs
    if args.rest:
        done = {d.name for d in (PIPELINE / "translations").iterdir()
                if (d / "_global.json").is_file()} if (PIPELINE / "translations").is_dir() else set()
        langs = [l for l in LANG_NAMES if l not in done and l not in langs]
    if not langs:
        ap.error("informe --langs ou --rest")
    print(f"idiomas na fila ({len(langs)}): {', '.join(langs)} "
          f"| paralelo: {args.parallel}")

    with ThreadPoolExecutor(max_workers=args.parallel) as ex:
        futs = {ex.submit(run_lang, l): l for l in langs}
        for fut in as_completed(futs):
            lang, rc, qa_tail = fut.result()
            status = "OK" if rc == 0 else f"FALHOU rc={rc}"
            print(f"\n===== {lang}: tradução {status} =====")
            print(qa_tail)


if __name__ == "__main__":
    main()
