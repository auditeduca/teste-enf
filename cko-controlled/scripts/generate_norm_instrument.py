#!/usr/bin/env python3
"""Project the COFEN Nota Técnica 6/2025 Drive package into one HOLD instrument.

Read-only of Drive. No HTTP ingest. No Vigente. One template → one HTML.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from norm_kernel import render_instrument, sha256_text, validate_instrument, write_json  # noqa: E402

INSTRUMENT_ID = "BR_FED_COFEN_NOTATEC_2025_N_00006"
DRIVE_FOLDER = "1zetnfRWES5wvUzpEsa1I1cbiziec6FKw"
DRIVE_ATOMS = "1bSsCCUoloaRbIh5crjXbmGb5YxrdaRpv"
DRIVE_ATOMS_SHA256 = "5c070b863f6034f18a1c553a838d7b13ff1966cdd42db92b3829338e83bd50da"

# Literal devices observed in NOTATEC_2025_N_00006_ATOMOS_V1.jsonl (Drive, read-only).
# Official act text is not copyright-protected (Lei 9.610/1998, art. 8, IV).
RAW_ATOMS = [
    ("EPIGRAFE_001", "epigrafe", "Epígrafe", "NOTA TÉCNICA Nº 6/2025/PLENÁRIO", "IDENTICO_NORMALIZADO"),
    ("IDENTIFICACAO_PROCESSO_001", "identificacao_processo", "Identificação do processo", "Processo n° 00196.004345/2025-59", "IDENTICO_NORMALIZADO"),
    ("SECAO_001", "secao", "1. ASSUNTO", "1. ASSUNTO", "IDENTICO_NORMALIZADO"),
    ("ITEM_001", "item", "Item 1.1", "1.1 Produção de Pareceres Fundamentados e Individualização de Condutas nos Processos Ético-Disciplinares.", "IDENTICO_NORMALIZADO"),
    ("SECAO_002", "secao", "2. REFERÊNCIAS", "2. REFERÊNCIAS", "IDENTICO_NORMALIZADO"),
    ("REFERENCIA_001", "referencia", "Referência 1", "2.1 Código de Processo Ético – Resolução Cofen nº 706/2022.", "IDENTICO_NORMALIZADO"),
    ("REFERENCIA_002", "referencia", "Referência 2", "2.2 Código de Ética – Resolução Cofen nº 564/2017.", "IDENTICO_NORMALIZADO"),
    ("SECAO_003", "secao", "3. SUMÁRIO EXECUTIVO", "3. SUMÁRIO EXECUTIVO", "IDENTICO_NORMALIZADO"),
    (
        "ITEM_002",
        "item",
        "Item 3.1",
        "3.1 Esta nota técnica destaca a importância da individualização das condutas dos denunciados nos pareceres dos relatores nas fases de admissibilidade e de julgamento de processos éticos e nos relatórios das comissões de instrução. Reforça a competência dos relatores em identificar e especificar as ações ou omissões de cada denunciado, enquadrando-as nos dispositivos do Código de Ética. Garantindo, assim, uma avaliação justa, facilitando a investigação pela comissão de instrução, permitindo a identificação de agravantes e atenuantes, e que no julgamento final, a aplicação de penalidades se baseie em provas cabais, com uma análise detalhada das condutas e da culpabilidade de cada denunciado. A falta de fundamentação e de individualização das condutas pode ser observada em diversos relatórios elaborados pela área de processos éticos do Cofen após visitas técnicas aos Regionais e durante análise pelo Plenário do Cofen, como instância recursal, de procedimentos e processos ético-disciplinares.",
        "IDENTICO_NORMALIZADO",
    ),
    ("SECAO_004", "secao", "4. ANÁLISE", "4. ANÁLISE", "IDENTICO_NORMALIZADO"),
    (
        "ITEM_003",
        "item",
        "Item 4.1",
        "4.1 Na fase de admissibilidade, uma vez distribuído o processo para relatoria, deve o relator, em seu parecer, havendo mais de um denunciado, identificar cada um deles e individualizar as condutas a eles atribuídas, conforme conste na denúncia, deixando claras as possíveis ações ou omissões que cada um pode ter praticado, promovendo em seguida o enquadramento das condutas nos respectivos dispositivos do Código de Ética. Mesmo que as condutas atribuídas aos denunciados sejam as mesmas, deve o relator identificá-las para cada um deles. Tal procedimento se mostra essencial para uma perfeita avaliação possibilitando, assim, um julgamento isonômico e igualitário, apenas diferenciando a condição pessoal de cada denunciado no que se refere, quando do julgamento final, da identificação de possíveis agravantes e/ou atenuantes, e na medida de sua culpabilidade. Com a correta individualização das condutas com seus respectivos enquadramentos no Código de Ética.",
        "IDENTICO_NORMALIZADO",
    ),
    (
        "ITEM_004",
        "item",
        "Item 4.2",
        "4.2 A comissão de instrução terá maior facilidade e clareza para investigar os fatos da denúncia, emitindo relatório final que não deixe dúvidas sobre a participação de cada um dos denunciados. A individualização da conduta é essencial para a correta aplicação do Código de Ética, pois define a responsabilidade de cada denunciado envolvido na prática considerada antiética. No mesmo sentido, o relator do julgamento final também promoverá, necessariamente, a individualização, com narrativa clara das ações perpetradas por cada um dos denunciados, e o correto enquadramento nos artigos do Código de Ética.",
        "IDENTICO_NORMALIZADO",
    ),
    (
        "ITEM_005",
        "item",
        "Item 4.3",
        "4.3 É de se esclarecer que quando da admissibilidade esta pode ser decidida com base em indícios que sustentem e justifiquem a abertura do processo ético. Já no julgamento final do processo pelo Plenário do conselho, possível aplicação de penalidade ética deve, necessariamente, se fundar em prova cabal e definitiva, não se prestando meros indícios como fundamento para uma condenação, mesmo se a sanção for a mais leve prevista no código. Para tanto, é preciso que o relator final identifique a conduta de cada denunciado, aponte as provas do cometimento da infração por cada um deles, promova o enquadramento da conduta segundo os artigos relacionados à infração cometida, analise a situação individual no que se refere a atenuantes/agravantes, além de verificar a medida da culpabilidade de cada um.",
        "IDENTICO_NORMALIZADO",
    ),
    ("SECAO_005", "secao", "5. CONCLUSÃO", "5. CONCLUSÃO", "IDENTICO_NORMALIZADO"),
    (
        "ITEM_006",
        "item",
        "Item 5.1",
        "5.1 A falta de individualização das condutas dos denunciados pode levar a várias consequências negativas. Primeiramente, pode resultar em uma avaliação injusta, pois não diferencia as ações ou omissões específicas de cada indivíduo, comprometendo a isonomia do julgamento. Além disso, dificulta a identificação de agravantes e atenuantes, o que pode levar à penalidades inadequadas. A investigação também se torna menos clara, dificultando a elaboração de um relatório final preciso. Por fim, a aplicação do Código de Ética pode ser comprometida, já que a responsabilidade de cada denunciado não é claramente definida, podendo resultar em decisões injustas ou equivocadas.",
        "IDENTICO_NORMALIZADO",
    ),
    (
        "ITEM_007",
        "item",
        "Item 5.2",
        "5.2 A produção de pareceres fundamentados e a individualização das condutas são cruciais para assegurar a justiça e a eficácia nos processos éticos. A aplicação rigorosa dessas diretrizes garante que cada denunciado seja avaliado de maneira justa e imparcial, com decisões baseadas em provas sólidas e definitivas. Esse procedimento não apenas promove a transparência e a equidade, mas também fortalece a confiança no sistema de ética profissional.",
        "EQUIVALENTE_ORDEM_OU_QUEBRA_DIFERENTE",
    ),
    (
        "NOTA_RODAPE_001",
        "nota_rodape",
        "Nota de rodapé 1",
        "*Nota Técnica elaborada por Alberto Jorge Santiago Cabral, Chefe da Assessoria Legislativa; Márcio Raleigue de Abreu Lima Verde, Chefe da Divisão de Processos Éticos; e Angélica Rogerio de Miranda Pontes, Chefe do Setor de Análise e Controle de Processos Éticos; tendo sido aprovada na 220ª Reunião Ordinária de Diretoria, em 5 de setembro de 2025.",
        "IDENTICO_NORMALIZADO",
    ),
    ("LOCAL_DATA_001", "local_data", "Local e data", "Brasília, 12 de novembro de 2025.", "IDENTICO_NORMALIZADO"),
    ("ASSINATURA_001", "assinatura", "Assinatura", "MANOEL CARLOS NERI DA SILVA / Coren-RO 63.592-ENF-IR / Presidente", "IDENTICO_NORMALIZADO"),
]


def payload() -> dict:
    atoms = []
    for index, (suffix, tipo, locator, text, pdf) in enumerate(RAW_ATOMS, start=1):
        atoms.append(
            {
                "id": f"{INSTRUMENT_ID}_{suffix}",
                "order": index,
                "type": tipo,
                "locator": locator,
                "text": text,
                "sha256": sha256_text(text),
                "status": "VERIFY_PENDING",
                "pdf_conference": pdf,
            }
        )
    return {
        "id": INSTRUMENT_ID,
        "kind": "normative_instrument",
        "template_id": "norm-instrument",
        "title": "NOTA TÉCNICA Nº 6/2025/PLENÁRIO — Cofen",
        "status": "VERIFY_PENDING",
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "assigns_vigencia": False,
        "clinical_promotion": "DENIED",
        "b9": "HOLD / NOT_RELEASED",
        "drive_writes": 0,
        "supabase_ddl": 0,
        "source": {
            "authority": "Conselho Federal de Enfermagem",
            "url": "https://www.cofen.gov.br/nota-tecnica-no-6-2025-plenario/",
            "drive_folder_id": DRIVE_FOLDER,
            "drive_atoms_id": DRIVE_ATOMS,
            "drive_atoms_sha256": DRIVE_ATOMS_SHA256,
            "drive_writes": 0,
            "html_scraped_not_used": "NOTATEC_2025_N_00006_PAGINA_SITE.html (446809 bytes) not copied",
        },
        "fechamento": {
            "apto": False,
            "status": "PENDENCIAS",
            "findings": ["C001", "C002"],
        },
        "atoms": atoms,
        "materialization": {
            "pages_from_atoms": 1,
            "html_files_per_atom": 0,
            "template": "norm-instrument",
        },
    }


def generate() -> dict:
    doc = payload()
    errors = validate_instrument(doc)
    if errors:
        raise SystemExit("FAIL: " + "; ".join(errors))
    write_json(PUBLIC / "data" / "norms" / f"{INSTRUMENT_ID}.json", doc)
    (PUBLIC / "cko-norma.html").write_text(render_instrument(doc), encoding="utf-8")
    return doc


def main() -> None:
    doc = generate()
    print(f"norm HOLD {doc['id']} atoms={len(doc['atoms'])} pages=1")


if __name__ == "__main__":
    main()
