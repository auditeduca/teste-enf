#!/usr/bin/env python3
"""Fase 3 — Tradução clínica única por calculadora, via API DeepSeek.

Para cada página, traduz o conteúdo clínico que o dicionário comum não cobre:
tool-config completo (overview, inputs, interpretação, SAE, evidências,
learning, FAQ, about), SEO (title/description/h1/subtitle) e os textos
estáticos únicos do corpo (unique_texts do scanner).

Fontes: i18n-pipeline/extracted/pages/{page}.json (scanner, Fase 1).
Destino: reference-website/{lang}/{page}.html (gerado na Fase 2).
Memória de tradução: i18n-pipeline/translations/{lang}/{page}.json
(review_status: "machine" — revisão humana pendente, cf. convenção
translation_tier do NKOS).

Uso:
  python translate_clinical.py --lang es --pages glasgow.html apgar.html
  python translate_clinical.py --lang es --pages glasgow.html --dry-run
Requer DEEPSEEK_API_KEY (env ou C:/Github/CALENF-NKD/.env).
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent
SITE = PIPELINE.parent / "reference-website"
ENV_FILE = Path("C:/Github/CALENF-NKD/.env")

API_URL = "https://api.deepseek.com/chat/completions"

# Nomes de idioma para o prompt (dir -> descrição)
LANG_NAMES = {
    "es": "español latinoamericano (es-419)",
    "en": "inglês (en)",
    "fr": "francês (fr)",
    "de": "alemão (de)",
    "it": "italiano (it)",
    "zh": "chinês simplificado (zh-CN)",
    "ja": "japonês (ja)",
    "ar": "árabe padrão moderno (ar)",
    "hi": "hindi (hi-IN)",
    "ru": "russo (ru-RU)",
    "ko": "coreano (ko-KR)",
    "tr": "turco (tr-TR)",
    "pl": "polonês (pl-PL)",
    "nl": "holandês (nl-NL)",
    "sv": "sueco (sv-SE)",
    "no": "norueguês bokmål (no-NO)",
    "da": "dinamarquês (da-DK)",
    "fi": "finlandês (fi-FI)",
    "cs": "tcheco (cs-CZ)",
    "hu": "húngaro (hu-HU)",
    "ro": "romeno (ro-RO)",
    "bg": "búlgaro (bg-BG)",
    "hr": "croata (hr-HR)",
    "sr": "sérvio (sr-RS)",
    "sl": "esloveno (sl-SI)",
    "uk": "ucraniano (uk-UA)",
    "vi": "vietnamita (vi-VN)",
    "th": "tailandês (th-TH)",
    "id": "indonésio (id-ID)",
}

# Chaves do tool-config cujos valores string NÃO devem ser traduzidos
SKIP_KEYS = {
    "id", "code", "slug", "version", "status", "canonical", "categoryHref",
    "icon", "color", "riskLevel", "complexity", "evidenceLevel", "emoji",
    "sublabel", "values", "defaultValue", "correct", "min", "max",
    "originalAuthors", "organizations", "references", "type", "decimals",
}


def load_env() -> None:
    if os.environ.get("DEEPSEEK_API_KEY"):
        return
    candidates = [
        ENV_FILE,
        PIPELINE.parent / ".env",
        PIPELINE.parent / "NIFS" / ".env",
        Path(os.environ.get("CALENF_ENV_FILE", "")),
    ]
    for path in candidates:
        if not path or not Path(path).is_file():
            continue
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            m = re.match(r"^(\w+)=(.+)$", line.strip())
            if m and m.group(1) not in os.environ:
                os.environ[m.group(1)] = m.group(2)
        if os.environ.get("DEEPSEEK_API_KEY"):
            return
    if not os.environ.get("DEEPSEEK_API_KEY"):
        sys.exit("DEEPSEEK_API_KEY não encontrada (env ou .env)")


def collect_strings(node, skip=False, out=None):
    """Coleta strings traduzíveis do tool_config, respeitando SKIP_KEYS."""
    if out is None:
        out = []
    if isinstance(node, dict):
        for k, v in node.items():
            collect_strings(v, skip or k in SKIP_KEYS, out)
    elif isinstance(node, list):
        for v in node:
            collect_strings(v, skip, out)
    elif isinstance(node, str) and not skip:
        s = node.strip()
        if s and not s.isdigit():
            out.append(node)
    return out


def apply_translations(node, tmap, skip=False):
    if isinstance(node, dict):
        return {k: apply_translations(v, tmap, skip or k in SKIP_KEYS) for k, v in node.items()}
    if isinstance(node, list):
        return [apply_translations(v, tmap, skip) for v in node]
    if isinstance(node, str) and not skip:
        return tmap.get(node, node)
    return node


def deepseek_translate(strings: list[str], lang_desc: str, proper_nouns: list[str]) -> dict[str, str]:
    """Traduz lista de strings pt-BR -> idioma alvo. Retorna {original: traduzida}."""
    api_key = os.environ["DEEPSEEK_API_KEY"]
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
    system = (
        "Você é tradutor especializado em enfermagem e terminologia clínica. "
        f"Traduza do português brasileiro para {lang_desc}.\n"
        "Regras:\n"
        "- Use terminologia clínica oficial no idioma alvo (NANDA-I, NOC, NIC, CIPE quando aplicável).\n"
        "- NÃO traduza nomes próprios de escalas e escores (ex.: "
        + ", ".join(proper_nouns[:40]) + ").\n"
        "- Preserve exatamente: tags HTML, entidades, quebras de linha \\n, bullets •, números, "
        "unidades, siglas (GCS, SpO2, UTI use o equivalente local se consagrado).\n"
        "- Responda SOMENTE com JSON válido: as mesmas chaves numéricas recebidas, valores traduzidos."
    )
    result: dict[str, str] = {}
    todo = [s for s in dict.fromkeys(strings)]  # dedupe preservando ordem
    # chunks de ~3500 caracteres
    chunks, cur, size = [], [], 0
    for s in todo:
        if cur and size + len(s) > 3500:
            chunks.append(cur)
            cur, size = [], 0
        cur.append(s)
        size += len(s)
    if cur:
        chunks.append(cur)

    for ci, chunk in enumerate(chunks, 1):
        remaining = {str(i): s for i, s in enumerate(chunk)}
        for attempt in range(3):
            if not remaining:
                break
            payload = {
                "model": model,
                "thinking": {"type": "disabled"},
                "temperature": 0.2,
                "max_tokens": 8000,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": json.dumps(remaining, ensure_ascii=False)},
                ],
            }
            try:
                req = urllib.request.Request(
                    API_URL, data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json",
                             "Authorization": f"Bearer {api_key}"})
                with urllib.request.urlopen(req, timeout=180) as resp:
                    body = json.load(resp)
                trans = json.loads(body["choices"][0]["message"]["content"])
                # aceita o que veio válido; re-pede só o que faltou
                for k, v in trans.items():
                    if k in remaining and isinstance(v, str) and v.strip():
                        result[remaining.pop(k)] = v
                if remaining:
                    print(f"    chunk {ci} tentativa {attempt + 1}: "
                          f"faltaram {len(remaining)} chaves, re-pedindo")
                    time.sleep(2)
                else:
                    print(f"    chunk {ci}/{len(chunks)}: {len(chunk)} strings OK")
            except Exception as e:
                print(f"    chunk {ci} tentativa {attempt + 1} falhou: {e}")
                time.sleep(3 * (attempt + 1))
        if remaining:
            print(f"    AVISO chunk {ci}: {len(remaining)} strings sem tradução "
                  f"(verify_agent cobre na verificação)")
    return result


def deepseek_judge(strings: list[str], lang_desc: str, proper_nouns: list[str]) -> dict[str, dict]:
    """Julga strings que ficaram idênticas ao pt na versão traduzida.
    Retorna {string: {"action": "keep"|"translate", "translation": str, "reason": str}}."""
    api_key = os.environ["DEEPSEEK_API_KEY"]
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
    system = (
        "Você é revisor de tradução clínica de enfermagem (português brasileiro -> "
        f"{lang_desc}). Cada string abaixo ficou IDÊNTICA ao português na página "
        "traduzida. Para cada chave, decida:\n"
        "- \"keep\": a forma é correta também no idioma alvo (cognato exato, nome "
        "próprio de escala/instituição, código, citação bibliográfica que deve "
        "permanecer no original).\n"
        "- \"translate\": ficou sem tradução — e forneça a tradução.\n"
        "Nomes próprios que nunca se traduzem: " + ", ".join(proper_nouns[:40]) + ".\n"
        "Responda SOMENTE JSON: {\"0\": {\"action\": \"keep\"}, "
        "\"1\": {\"action\": \"translate\", \"translation\": \"...\"}, ...}"
    )
    result: dict[str, dict] = {}
    todo = list(dict.fromkeys(strings))
    chunks, cur, size = [], [], 0
    for s in todo:
        if cur and size + len(s) > 3000:
            chunks.append(cur); cur, size = [], 0
        cur.append(s); size += len(s)
    if cur:
        chunks.append(cur)
    for ci, chunk in enumerate(chunks, 1):
        payload = {
            "model": model,
            "thinking": {"type": "disabled"},
            "temperature": 0.1,
            "max_tokens": 8000,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(
                    {str(i): s for i, s in enumerate(chunk)}, ensure_ascii=False)},
            ],
        }
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    API_URL, data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json",
                             "Authorization": f"Bearer {api_key}"})
                with urllib.request.urlopen(req, timeout=180) as resp:
                    body = json.load(resp)
                verdicts = json.loads(body["choices"][0]["message"]["content"])
                for i, s in enumerate(chunk):
                    v = verdicts.get(str(i)) or {}
                    if isinstance(v, dict) and v.get("action") in ("keep", "translate"):
                        result[s] = v
                    else:
                        result[s] = {"action": "keep", "reason": "resposta inválida do juiz"}
                print(f"    juiz chunk {ci}/{len(chunks)}: {len(chunk)} strings")
                break
            except Exception as e:
                print(f"    juiz chunk {ci} tentativa {attempt + 1} falhou: {e}")
                if attempt == 2:
                    raise
                time.sleep(3 * (attempt + 1))
    return result


def swap_tool_config(html: str, cfg: dict) -> tuple[str, bool]:
    blob = json.dumps(cfg, ensure_ascii=False, separators=(", ", ": "))
    blob = blob.replace("</", "<\\/")  # evita fechar o <script> prematuramente
    rx = re.compile(r'(<script[^>]*id=["\']tool-config["\'][^>]*>).*?(</script>)', re.S)
    new, n = rx.subn(lambda m: m.group(1) + blob + m.group(2), html, count=1)
    return new, n == 1


def replace_text(html: str, pairs: list[tuple[str, str]]) -> tuple[str, int]:
    """Substituição exata, das strings mais longas para as mais curtas."""
    count = 0
    for src, dst in sorted(pairs, key=lambda p: -len(p[0])):
        if src and dst and src != dst and src in html:
            html = html.replace(src, dst)
            count += 1
    return html, count


def replace_bounded(html: str, pairs: list[tuple[str, str]]) -> tuple[str, int]:
    """Substituição com fronteira de palavra (não casa no meio de outra
    palavra), para os nós de texto do scanner profundo."""
    count = 0
    for src, dst in sorted(pairs, key=lambda p: -len(p[0])):
        if not src or not dst or src == dst:
            continue
        rx = re.compile(r"(?<![A-Za-zÀ-ÿ])" + re.escape(src) + r"(?![A-Za-zÀ-ÿ])")
        html, n = rx.subn(dst.replace("\\", "\\\\"), html)
        count += 1 if n else 0
    return html, count


def global_tm_path(lang: str) -> Path:
    return PIPELINE / "translations" / lang / "_global.json"


def load_global_tm(lang: str) -> dict[str, str]:
    p = global_tm_path(lang)
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8")).get("translations", {})
    return {}


def save_global_tm(lang: str, tm: dict[str, str]) -> None:
    p = global_tm_path(lang)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"lang": lang, "review_status": "machine",
                             "translations": tm}, ensure_ascii=False, indent=1),
                 encoding="utf-8")


def seed_global_from_pages(lang: str) -> None:
    """Merge das memórias por página já existentes no dicionário global."""
    gtm = load_global_tm(lang)
    before = len(gtm)
    for f in (PIPELINE / "translations" / lang).glob("*.json"):
        if f.name == "_global.json":
            continue
        gtm.update(json.loads(f.read_text(encoding="utf-8")).get("translations", {}))
    save_global_tm(lang, gtm)
    print(f"[{lang}] dicionário global: {before} -> {len(gtm)} entradas")


META_KEYS = ["description", "keywords", "og:title", "og:description",
             "twitter:title", "twitter:description"]


def _swap_meta_content(html: str, key: str, value: str) -> str:
    value = value.replace('"', "&quot;")
    rx = re.compile(r'<meta\b[^>]*>', re.I)
    key_rx = re.compile(r'(?:name|property)=["\']' + re.escape(key) + r'["\']', re.I)

    def fix(m):
        tag = m.group(0)
        if not key_rx.search(tag):
            return tag
        return re.sub(r'content=(["\']).*?\1', f'content="{value}"', tag, count=1)

    return rx.sub(fix, html)


def _map_json_strings(node, tmap):
    if isinstance(node, dict):
        return {k: _map_json_strings(v, tmap) for k, v in node.items()}
    if isinstance(node, list):
        return [_map_json_strings(v, tmap) for v in node]
    if isinstance(node, str):
        return tmap.get(node, node)
    return node


def swap_head_structural(html: str, root_html: str, tmap: dict, lang: str) -> str:
    """Troca <title>, metas e JSON-LD usando os valores da página raiz pt
    como fonte (estável), traduzidos pelo dicionário. Idempotente — repara
    inclusive páginas danificadas por substituições parciais anteriores."""
    t = re.search(r"<title>(.*?)</title>", root_html, re.S)
    if t and t.group(1).strip() in tmap:
        html = re.sub(r"<title>.*?</title>",
                      lambda m: f"<title>{tmap[t.group(1).strip()]}</title>",
                      html, count=1, flags=re.S)
    for key in META_KEYS:
        m = re.search(r'<meta\b[^>]*(?:name|property)=["\']' + re.escape(key)
                      + r'["\'][^>]*>', root_html, re.I)
        if not m:
            continue
        v = re.search(r'content=(["\'])(.*?)\1', m.group(0), re.S)
        if v and v.group(2) in tmap:
            html = _swap_meta_content(html, key, tmap[v.group(2)])
    ld_rx = re.compile(r'(<script[^>]*application/ld\+json[^>]*>)(.*?)(</script>)', re.S | re.I)
    root_lds = ld_rx.findall(root_html)
    tgt_lds = list(ld_rx.finditer(html))
    if len(root_lds) == len(tgt_lds):
        out, pos = [], 0
        for (_, raw, _), m in zip(root_lds, tgt_lds):
            try:
                data = _map_json_strings(json.loads(raw), tmap)
                blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
            except Exception:
                continue
            out.append(html[pos:m.start(2)])
            out.append(blob)
            pos = m.end(2)
        out.append(html[pos:])
        html = "".join(out)
    return html


def translate_page(page: str, lang: str, dry: bool) -> None:
    name = page[:-5] if page.endswith(".html") else page
    extracted = PIPELINE / "extracted" / "pages" / f"{name}.json"
    target = SITE / lang / f"{name}.html"
    if not extracted.is_file():
        print(f"[{name}] SEM extração do scanner — pulado"); return
    if not target.is_file():
        print(f"[{name}] página {lang}/{name}.html não existe — pulado"); return

    data = json.loads(extracted.read_text(encoding="utf-8"))
    seo = data.get("seo") or {}
    cfg = data.get("tool_config")
    uniq = [t for _, t in (data.get("unique_texts") or [])]

    deep_file = PIPELINE / "extracted" / "pages_deep" / f"{name}.json"
    deep: list[str] = []
    if deep_file.is_file():
        dd = json.loads(deep_file.read_text(encoding="utf-8"))
        deep = list(dict.fromkeys((dd.get("texts") or []) + (dd.get("attrs") or [])))

    strings = collect_strings(cfg) if cfg else []
    strings += [v for v in seo.values() if isinstance(v, str) and v.strip()]
    strings += [u for u in uniq if u and u.strip()]
    strings += deep
    strings = list(dict.fromkeys(strings))
    if not strings:
        print(f"[{name}] nada a traduzir"); return
    print(f"[{name}] {len(strings)} strings únicas -> {lang}")

    proper = []
    pn_file = PIPELINE / "extracted" / "common_proper_nouns.json"
    if pn_file.is_file():
        pn = json.loads(pn_file.read_text(encoding="utf-8"))
        proper = pn if isinstance(pn, list) else list(pn)

    # dicionário global do idioma (corpus traduzido) + memória por página
    gtm = load_global_tm(lang)
    tmap: dict[str, str] = dict(gtm)
    tm_file = PIPELINE / "translations" / lang / f"{name}.json"
    if tm_file.is_file():
        tmap.update(json.loads(tm_file.read_text(encoding="utf-8")).get("translations", {}))
    # correções do verify_agent têm precedência (já passaram pelo juiz)
    fixes_f = PIPELINE / "translations" / lang / "_verify_fixes.json"
    if fixes_f.is_file():
        tmap.update(json.loads(fixes_f.read_text(encoding="utf-8")).get("translate", {}))
    missing = [s for s in strings if s not in tmap]
    if missing:
        new = deepseek_translate(missing, LANG_NAMES.get(lang, lang), proper)
        tmap.update(new)
        gtm.update(new)
        save_global_tm(lang, gtm)
    else:
        print(f"[{name}] 100% reaproveitado do dicionário global/memória")

    tm_dir = PIPELINE / "translations" / lang
    tm_dir.mkdir(parents=True, exist_ok=True)
    (tm_dir / f"{name}.json").write_text(
        json.dumps({"page": f"{name}.html", "lang": lang, "review_status": "machine",
                    "translations": tmap}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    if dry:
        print(f"[{name}] dry-run: memória salva em translations/{lang}/{name}.json"); return

    html = target.read_text(encoding="utf-8")
    subs = 0
    if cfg:
        new_cfg = apply_translations(cfg, tmap)
        html, ok = swap_tool_config(html, new_cfg)
        subs += 1 if ok else 0
        if not ok:
            print(f"[{name}] AVISO: bloco tool-config não encontrado na página alvo")
    # corpo: seo + textos únicos + strings do config pré-renderizadas no HTML
    # (breadcrumb, badge, painel de resultados); mínimo de 12 chars para não
    # colidir com substrings de palavras comuns
    body_sources = list(seo.values()) + uniq + [s for s in strings if len(s) >= 12]
    body_pairs = [(s, tmap[s]) for s in dict.fromkeys(body_sources)
                  if isinstance(s, str) and s in tmap]
    html, n = replace_text(html, body_pairs)
    deep_pairs = [(s, tmap[s]) for s in deep if s in tmap]
    html, nd = replace_bounded(html, deep_pairs)
    # passada final: strings longas em qualquer contexto restante (JSON-LD,
    # metas não capturadas) — ≥15 chars não colidem com substrings de palavras
    html, nf = replace_text(html, [(s, t) for s, t in tmap.items() if len(s) >= 15])
    root_file = SITE / f"{name}.html"
    if root_file.is_file():
        html = swap_head_structural(html, root_file.read_text(encoding="utf-8"), tmap, lang)
    html = html.replace('"inLanguage": "pt-BR"', f'"inLanguage": "{lang}"')
    subs += n + nd + nf
    target.write_text(html, encoding="utf-8", newline="")
    print(f"[{name}] gravado {lang}/{name}.html — tool-config trocado + "
          f"{n} substituições diretas + {nd} profundas")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--pages", nargs="*", default=[])
    ap.add_argument("--all", action="store_true", help="todas as páginas extraídas")
    ap.add_argument("--seed", action="store_true",
                    help="só mescla memórias por página no dicionário global")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.seed:
        seed_global_from_pages(args.lang)
        return
    load_env()
    pages = args.pages
    if args.all:
        pages = sorted(f.stem + ".html" for f in (PIPELINE / "extracted" / "pages").glob("*.json"))
    if not pages:
        ap.error("informe --pages ou --all")
    for p in pages:
        try:
            translate_page(p, args.lang, args.dry_run)
        except Exception as e:
            print(f"[{p}] ERRO: {e}")


if __name__ == "__main__":
    main()
