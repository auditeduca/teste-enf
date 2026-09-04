#!/usr/bin/env python3
"""Materialize the known CKO/CALENF controlled universe from the final report."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"

GLOBAL_SHA = "460128914264512dfd17161ba3c73ceeadd8da36775327e818f3c3ee3ab25d5a"

BLOCKS = [
    {
        "id": "B1",
        "name": "Agent Job Runtime",
        "control": "100% classificado",
        "coverage": "635/635 fields; 315/315 execution bindings",
        "pending": "HOLD: historico/transport/selection",
        "artifact_id": "ART-CKO-B1-AUD8L-FINAL-20260902",
        "version_id": "OV-CKO-B1-AUD8L-REPORT-1.0.1",
        "sha256": "e1b4be9b85d2b2a1fb7de4c1bd2933b573da39778b8ac444ed6adbe3576d7d6e",
        "checkpoint_id": "CP-CKO-B1-AUD8L-FINAL-20260902-001",
        "maturity": 75,
        "state": "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
        "holds": ["historico", "transport", "selection"],
    },
    {
        "id": "B2",
        "name": "Source Library",
        "control": "100% classificado",
        "coverage": "157/157 fontes; 159/159 fields",
        "pending": "154 HOLD_SCOPED; 3 N/A",
        "artifact_id": "ART-CKO-B2-AUD8L-FINAL-20260902",
        "version_id": "OV-CKO-B2-AUD8L-REPORT-1.0.0",
        "sha256": "eabdcff2483a1e8b77f2561e394e7b5ef922adcbffd975d9787fa349fb5c459c",
        "checkpoint_id": "CP-CKO-B2-AUD8L-FINAL-20260902-001",
        "maturity": 75,
        "state": "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
        "holds": ["HOLD_SCOPED:154", "N/A:3"],
    },
    {
        "id": "B3",
        "name": "Canonical Objects",
        "control": "100% classificado",
        "coverage": "84 objetos conhecidos; 96 registros",
        "pending": "12 unresolved + bindings/labels",
        "artifact_id": "ART-CKO-B3-AUD8L-FINAL-20260902",
        "version_id": "OV-CKO-B3-AUD8L-REPORT-1.0.1",
        "sha256": "924035b9d943879306fa39efdc548effa36ff669f3b8fe0a37887901915d2d68",
        "checkpoint_id": "CP-CKO-B3-AUD8L-FINAL-20260902-001",
        "maturity": 75,
        "state": "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
        "holds": ["unresolved_identities:12", "bindings", "labels"],
    },
    {
        "id": "B4",
        "name": "E2E Binding Registry",
        "control": "100% classificado",
        "coverage": "84/84 shared stack; 258/258 fields",
        "pending": "logica especifica + runtime",
        "artifact_id": "ART-CKO-B4-AUD8L-FINAL-20260902",
        "version_id": "OV-CKO-B4-AUD8L-REPORT-1.0.0",
        "sha256": "a31aaac4f510e48eb292aa0581e1f29a820d022f693c245a10b328116262d00f",
        "checkpoint_id": "CP-CKO-B4-AUD8L-FINAL-20260902-001",
        "maturity": 75,
        "state": "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
        "holds": ["specific_logic", "runtime"],
    },
    {
        "id": "B5",
        "name": "Digital Twin",
        "control": "100% classificado",
        "coverage": "137 nodes; 136 edges",
        "pending": "deployed/observed = HOLD",
        "artifact_id": "ART-CKO-B5-DIGITAL-TWIN-CANONICAL-20260902",
        "version_id": "OV-CKO-B5-DIGITAL-TWIN-1.0.0",
        "sha256": "276ccc008047ea540d8a502729e9f0e855543584bfb19254c07e6c318651927a",
        "checkpoint_id": "CP-CKO-B5-AUD8L-FINAL-20260902-001",
        "maturity": 50,
        "state": "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
        "holds": ["deployed", "observed"],
    },
    {
        "id": "B6.1",
        "name": "Clinical Vertical",
        "control": "100% classificado",
        "coverage": "77/77 objetos; 157/157 fields",
        "pending": "homologacao, rights, runtime",
        "artifact_id": "ART-CKO-B6C-AUD8L-FINAL-20260902",
        "version_id": "OV-CKO-B6C-AUD8L-REPORT-1.0.0",
        "sha256": "abc01d2e3e9a529a6b0188ab728d3e2848cd6c38302a5819f091e9087d72ca79",
        "checkpoint_id": "CP-CKO-B6C-AUD8L-FINAL-20260902-001",
        "maturity": 50,
        "state": "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
        "holds": ["homologacao", "rights", "runtime"],
    },
    {
        "id": "B6.2",
        "name": "Knowledge/Libraries",
        "control": "100% classificado",
        "coverage": "79/79 profiles; 9/9 domains",
        "pending": "rights, binding exato, release",
        "artifact_id": "ART-CKO-B6K-AUD8L-FINAL-20260902",
        "version_id": "OV-CKO-B6K-AUD8L-REPORT-1.0.0",
        "sha256": "d7721142755fa539ecc74989558505da0f37a919f7b890f833887b92d53847fe",
        "checkpoint_id": "CP-CKO-B6K-AUD8L-FINAL-20260902-001",
        "maturity": 50,
        "state": "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
        "holds": ["rights", "exact_binding", "release"],
    },
    {
        "id": "B6.3",
        "name": "Experience/Publication",
        "control": "100% classificado",
        "coverage": "12/12 pages; 30/30 locales",
        "pending": "A11y empirica, linguagem, rights",
        "artifact_id": "ART-CKO-B6E-AUD8L-FINAL-20260902",
        "version_id": "OV-CKO-B6E-AUD8L-REPORT-1.0.0",
        "sha256": "5f5d5fa791edf7be812c01aad5159b2c5186614e8ec781818590420e5ddb6ac4",
        "checkpoint_id": "CP-CKO-B6E-AUD8L-FINAL-20260902-001",
        "maturity": 50,
        "state": "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
        "holds": ["a11y_empirical", "language", "rights"],
    },
    {
        "id": "B6.4",
        "name": "Labor/WK",
        "control": "100% classificado",
        "coverage": "7/7 WK; 35/35 fields",
        "pending": "legal rule packs, jurisdicao",
        "artifact_id": "ART-CKO-B6L-AUD8L-FINAL-20260902",
        "version_id": "OV-CKO-B6L-AUD8L-REPORT-1.0.0",
        "sha256": "dc4bc881941a8bc11cedee407e91a8cf40307fc668d3fd97bdf4b09a369ec69e",
        "checkpoint_id": "CP-CKO-B6L-AUD8L-FINAL-20260902-001",
        "maturity": 50,
        "state": "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
        "holds": ["legal_rule_packs", "jurisdiction"],
    },
    {
        "id": "B7",
        "name": "Learning/Recertification",
        "control": "100% classificado",
        "coverage": "336 learnings atuais; recert 1 FAIL",
        "pending": "201 pending reperformance",
        "artifact_id": "ART-CKO-B7-AUD8L-FINAL-20260902",
        "version_id": "OV-CKO-B7-AUD8L-REPORT-1.0.0",
        "sha256": "561395e658ad2f803376dda32ee0aeae4cdf403f596b763a2b6f7f6f3504e44b",
        "checkpoint_id": "CP-CKO-B7-AUD8L-FINAL-20260902-001",
        "maturity": 25,
        "state": "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
        "holds": ["recert_FAIL", "pending_reperformance:201"],
    },
    {
        "id": "B8",
        "name": "Runtime Assurance",
        "control": "100% classificado",
        "coverage": "129 tests; 131 validations",
        "pending": "browser/deploy/security HOLD",
        "artifact_id": "ART-CKO-B8-AUD8L-FINAL-20260902",
        "version_id": "OV-CKO-B8-AUD8L-REPORT-1.0.0",
        "sha256": "28dfd258812ed98b2a8ff636db0d9c6c1e9e0d4c44ed0f2576c57257e9785e2c",
        "checkpoint_id": "CP-CKO-B8-AUD8L-FINAL-20260902-001",
        "maturity": 50,
        "state": "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
        "holds": ["browser", "deploy", "security"],
    },
    {
        "id": "B9",
        "name": "Release Fan-In",
        "control": "100% classificado",
        "coverage": "release denominator fechado",
        "pending": "HOLD / NOT_RELEASED",
        "artifact_id": "ART-CKO-B9-AUD8L-FINAL-20260902",
        "version_id": "OV-CKO-B9-AUD8L-REPORT-1.0.0",
        "sha256": "b648ad2d161e866db7157ee57ec7058669d15eda2fd3d858755c3294687bbcab",
        "checkpoint_id": "CP-CKO-B9-AUD8L-FINAL-20260902-001",
        "maturity": 0,
        "state": "HOLD_NOT_RELEASED",
        "holds": ["HOLD", "NOT_RELEASED"],
        "release": "NOT_RELEASED",
    },
    {
        "id": "B10",
        "name": "Nurse-PaLM Formalization",
        "control": "100% formalizado",
        "coverage": "44 layers; 8 capabilities; 219 fields",
        "pending": "operacional = NOT_ASSERTED",
        "artifact_id": "ART-CKO-B10-AUD8L-FINAL-20260902",
        "version_id": "OV-CKO-B10-AUD8L-REPORT-1.0.0",
        "sha256": "977ea19691b572ebfba26722ee970f20327cccdd74e0c36dd6f6d1f334534fe1",
        "checkpoint_id": "CP-CKO-B10-AUD8L-FINAL-20260902-001",
        "maturity": 25,
        "state": "FORMALIZED_NOT_ASSERTED",
        "holds": ["operational_NOT_ASSERTED"],
        "operational": "NOT_ASSERTED",
    },
]

LENSES = [
    {"id": "AUD-360", "name": "AUD-360", "purpose": "Visao holistica do objeto, dependencias, riscos e evidencias."},
    {"id": "AUD-DIR", "name": "Direcional", "purpose": "Rastreabilidade direta MD/REG -> schema -> runtime."},
    {"id": "AUD-COMP", "name": "Complementar", "purpose": "Controles complementares e independencia funcional."},
    {"id": "AUD-INV", "name": "Inversa", "purpose": "Rastreabilidade inversa runtime/field -> MD/REG/source."},
    {"id": "AUD-DIAG", "name": "Diagonal", "purpose": "Cruza dominio, controle, evidence e estado."},
    {"id": "AUD-VERT", "name": "Vertical", "purpose": "Hierarquia e dependencias verticais."},
    {"id": "AUD-HOR", "name": "Horizontal", "purpose": "Consistencia entre pares/camadas."},
    {"id": "AUD-CIRC", "name": "Circular", "purpose": "Learning, regression, reperformance e reproducibilidade."},
]

PRIORITIES = [
    {
        "id": "P0-SEC",
        "priority": "P0",
        "domain": "Security / recertification",
        "evidence": "1 recertificacao FAIL; exposicao de SECURITY DEFINER registrada nas waves de runtime",
        "effect": "Bloqueia release ate hardening + nova reperformance.",
    },
    {
        "id": "P0-REL",
        "priority": "P0",
        "domain": "Release / runtime observado",
        "evidence": "B9 = HOLD / NOT_RELEASED; Nurse-PaLM operacional nao afirmado",
        "effect": "Exige deployment/readback/browser/mobile/performance observado.",
    },
    {
        "id": "P1-LEARN",
        "priority": "P1",
        "domain": "Learning backlog",
        "evidence": "201 learning records em PENDING_REPERFORMANCE",
        "effect": "Executar por ownership, regression test e recertification quando aplicavel.",
    },
    {
        "id": "P1-RIGHTS",
        "priority": "P1",
        "domain": "Rights / publication",
        "evidence": "13 holds globais de RIGHTS_PROVENANCE + gates derivados",
        "effect": "Nao publicar/reproduzir conteudo sem rights chain.",
    },
    {
        "id": "P1-CLIN",
        "priority": "P1",
        "domain": "Clinical",
        "evidence": "homologacao, rule packs, evidence e runtime observados em holds",
        "effect": "Nao converter classificacao tecnica em recomendacao clinica operacional.",
    },
    {
        "id": "P1-OUTBOX",
        "priority": "P1",
        "domain": "Outbox / ACK",
        "evidence": "296 eventos PENDING no readback final",
        "effect": "PENDING nao e ACK; transporte interno nao e action acknowledgment.",
    },
    {
        "id": "P2-ID",
        "priority": "P2",
        "domain": "Identity / binding legado",
        "evidence": "unresolved identities, field contracts e canonical bindings residuais",
        "effect": "Fechar por successor/versionamento, sem sobrescrever historico.",
    },
]

DRIVE = [
    {"name": "CKO-CALENF-FULL-MATERIALIZED-BACKUP-20260902.zip", "id": "1YSkh-x9RfHRshppfcVpChUnInh4hNYfG", "path": "My Drive / CKO-CALENF-FULL-MATERIALIZED-BACKUP-20260902.zip", "parent_known": True},
    {"name": "ALL-SHA256-MANIFEST-20260902.json", "id": "1Vs7l-m3d1nsSpmwlbkURsiu1a0eEseMg", "path": "My Drive / ALL-SHA256-MANIFEST-20260902.json", "parent_known": True},
    {"name": "CKO — START HERE Multiagent Shared Blackboard v1.0.1 — 2026-08-30", "id": "1TjFBRbguG2hFtg2uIKhFCdrJolbB3fyB95Oyg92tiaw", "path": "Google Drive (ID canonico; pasta pai nao exposta pela busca)", "parent_known": False},
    {"name": "CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE-v1.0.0", "id": "1iviD__hUDpiPOdMZ08gV-ooN9RF4ACyYZxKfYH_4EIw", "path": "Google Drive (ID canonico; pasta pai nao exposta pela busca)", "parent_known": False},
    {"name": "CKO-44-LAYER-GLOBAL-FANIN-ASSURANCE-v1.0.0", "id": "1OduAfQZGwZz1dPz-QGGbo990dgG1DHa7WfipRqFSvOk", "path": "Google Drive (ID canonico; pasta pai nao exposta pela busca)", "parent_known": False},
    {"name": "CKO_DESIGN_SYSTEM_MASTER_MAP_2026-08-08_v1_1_CONSOLIDADO.xlsx", "id": "1ylO4sEubIPytJJWNwCCQcRgGK1EBEyIf", "path": "My Drive / CKO_DESIGN_SYSTEM_MASTER_MAP_2026-08-08_v1_1_CONSOLIDADO.xlsx", "parent_known": True},
    {"name": "CKO_BACKUP_2026-08-28", "id": "1-h2dLv_aHoje7aV-W6ahzgl6_kcokRYi", "path": "My Drive / CKO_BACKUP_2026-08-28/", "parent_known": True},
    {"name": "CKO Backups", "id": "1abkGcvnwbybFUv6wZK6DOOZg8eBWNp7U", "path": "My Drive / CKO Backups/", "parent_known": True},
    {"name": "ChatGPT_Arquivo_Mestre_2026-08-22", "id": "1jJyX81hIZLZ2T3oKq4TSPm9Mge4UNSDp", "path": "My Drive / ChatGPT_Arquivo_Mestre_2026-08-22/", "parent_known": True},
    {"name": "Gestão de IAs e Studio CMS - Artefatos", "id": "1BqFCAzHSRzQJV30DTuIwiO_shGARKBin", "path": "My Drive / Gestão de IAs e Studio CMS - Artefatos/", "parent_known": True},
    {"name": "CKO_STATIC_PROJECT_COMPLETE_NURSE_PALM_RC_v6_5_0.zip", "id": "1qvHE3QNQ9aQB29pel5-V7e3c-Iral6zo", "path": "My Drive / CKO_STATIC_PROJECT_COMPLETE_NURSE_PALM_RC_v6_5_0.zip", "parent_known": True},
    {"name": "NURSE_PALM_21_LAYER_COMPLETENESS_MATRIX_v6_4_0.csv", "id": "1dlYNEsPGggbLCSCMSJE78aoEU73guabv", "path": "My Drive / NURSE_PALM_21_LAYER_COMPLETENESS_MATRIX_v6_4_0.csv", "parent_known": True},
    {"name": "NURSE_PALM_21_LAYER_COMPLETENESS_AUDIT_v6_4_0.json", "id": "1n8rUem3iFgg-ePKq7EtTMf6pGugEOgE9", "path": "My Drive / NURSE_PALM_21_LAYER_COMPLETENESS_AUDIT_v6_4_0.json", "parent_known": True},
    {"name": "CKO-PAGE-INSTITUTIONAL-WAVE2-v0.2.0.zip", "id": "1axsjjkYlnTaBPzBp9s8HeJ3e1aZKBgR4", "path": "My Drive / CKO-PAGE-INSTITUTIONAL-WAVE2-v0.2.0.zip", "parent_known": True},
    {"name": "CKO_DS_CANON_HEALTH_BRANDING_2026-08-30_v0.1.0.zip", "id": "1FRbPO67cn7W2fZNRY7xILauKYpuvd6wA", "path": "My Drive / CKO_DS_CANON_HEALTH_BRANDING_2026-08-30_v0.1.0.zip", "parent_known": True},
]

FOLDERS = [
    ("CKO_HANDOFF_ALDRETE_20260902", 123),
    ("aldrete_complete_v040", 16),
    ("aldrete_experience_v0611", 15),
    ("aldrete_runtime_and_templates_v062", 15),
    ("aldrete_runtime_and_templates_v063", 15),
    ("aldrete_runtime_and_templates_v061", 15),
    ("aldrete_runtime_and_templates_v065", 15),
    ("aldrete_runtime_and_templates_v064", 15),
    ("aldrete_experience_v0612", 13),
    ("[root]", 12),
    ("user-MKlyzIgUG5duD7FzphvXSf3T", 11),
    ("aldrete_experience_v0610", 11),
    ("aldrete_experience_v0613", 8),
    ("aldrete_remediation", 8),
    ("aldrete_experience_v0615", 8),
    ("aldrete_experience_v0614", 8),
    ("aldrete_experience_v069", 7),
    ("aldrete_runtime_shots_v050", 7),
    ("aldrete_experience_v052", 6),
    ("aldrete_experience_v051", 6),
    ("aldrete_experience_v050", 6),
    ("aldrete_experience_v060", 6),
    ("aldrete_runtime_and_templates_v060", 6),
    ("aldrete_experience_v068", 6),
    ("aldrete_experience_v063", 5),
    ("aldrete_experience_v061", 5),
    ("aldrete_experience_v062", 5),
    ("aldrete_experience_v065", 5),
    ("aldrete_experience_v064", 5),
    ("aldrete_reference_correction_v100", 5),
    ("aldrete_experience_v067", 5),
    ("aldrete_universal_v030", 4),
    ("aldrete_handoff_20260902", 4),
    ("aldrete_pdf_v070", 4),
    ("universal_tool", 4),
    ("aldrete_pdf_v071", 4),
    ("aldrete_og_v100", 3),
    ("aldrete_ds_ui_template_checker_v0612", 2),
    ("aldrete_asset_derivation_v0615", 2),
    ("aldrete_closure_20260902", 2),
    ("aldrete_article_binding_v0613", 2),
    ("aldrete_a11y_reperformance_v066", 2),
    ("hash_reconcile", 2),
    ("aldrete_i18n_checker", 2),
    ("aldrete_routes_v0615", 2),
    ("universal_tool_checker_v033", 2),
    ("aldrete_media_checker_v100", 2),
    ("aldrete_reliability_v0614", 2),
    ("aldrete_hcd_perf_obs_v0614", 2),
    ("aldrete_ds_checker", 1),
    ("aldrete-hash", 1),
    ("aldrete_layer_checker", 1),
    ("aldrete_final_holds_20260902", 1),
    ("fugulin_recovery", 1),
    ("md_field_recovery", 1),
    ("md_crosswalk", 1),
    ("universal_tool_checker_v031", 1),
    ("universal_tool_auditor_v032", 1),
]

UNKNOWN = [
    {"id": "UNK-DRIVE-PARENTS", "statement": "Pasta pai de alguns itens Google Drive nao foi exposta pelo conector; localizacao e Drive ID, sem fabricar pasta."},
    {"id": "UNK-DRIVE-OUTSIDE-SNAPSHOT", "statement": "O inventario de 449 arquivos e o snapshot materializado do manifesto 2026-09-02, nao o Drive inteiro do usuario."},
    {"id": "UNK-SUPABASE-PHYSICAL", "statement": "IDs Supabase sao localizacoes logicas controladas; nao sao arquivos fisicos isolados."},
    {"id": "UNK-PITR", "statement": "Backup materializado e baseline governada nao equivalem automaticamente a pg_dump/PITR full-restorable com restore test."},
    {"id": "UNK-OBSERVED-RUNTIME", "statement": "Deployment observado, browser/mobile empirico e performance observado permanecem HOLD."},
    {"id": "UNK-NURSEPALM-OPS", "statement": "Runtime operacional Nurse-PaLM nao foi afirmado (NOT_ASSERTED)."},
    {"id": "UNK-RIGHTS-CHAIN", "statement": "Cadeia de direitos de publicacao nao esta fechada (13 holds RIGHTS_PROVENANCE)."},
    {"id": "UNK-CLINICAL-HOMOLOG", "statement": "Homologacao clinica operacional nao foi convertida a partir da classificacao tecnica."},
    {"id": "UNK-A11Y-EMPIRICAL", "statement": "Acessibilidade empirica (B6.3) permanece em hold."},
    {"id": "UNK-SECURITY-RECERT", "statement": "1 recertificacao FAIL; SECURITY DEFINER exige hardening + reperformance."},
    {"id": "UNK-OUTBOX-ACK", "statement": "296 eventos PENDING no outbox; PENDING nao e ACK."},
    {"id": "UNK-HEATMAP-PRIMARY", "statement": "Heatmaps sao instrumentos de priorizacao; evidencia primaria permanece em checkpoints, findings, holds, versions e hashes."},
]


def residual_uncertainty() -> dict:
    """Quantify residual uncertainty X over the known control vs operational gap."""
    classified = 13
    released = 0
    recert_fail = 1
    holds = 211
    findings_open = 313
    pending_reperf = 201
    learnings = 336
    outbox_pending = 296
    rights_holds = 13
    unresolved_ids = 12

    control_gap = 0.0  # 13/13 classified
    release_gap = 1.0  # NOT_RELEASED
    recert_gap = 1.0 if recert_fail else 0.0
    reperf_gap = pending_reperf / learnings
    findings_weight = min(1.0, findings_open / 1000)
    outbox_gap = 1.0  # PENDING != ACK, none acknowledged in report
    rights_gap = 1.0 if rights_holds else 0.0
    identity_gap = unresolved_ids / 84

    weights = {
        "release_gap": 0.28,
        "recert_gap": 0.18,
        "reperf_gap": 0.14,
        "outbox_gap": 0.10,
        "rights_gap": 0.12,
        "findings_weight": 0.08,
        "identity_gap": 0.06,
        "control_gap": 0.04,
    }
    components = {
        "control_gap": control_gap,
        "release_gap": release_gap,
        "recert_gap": recert_gap,
        "reperf_gap": round(reperf_gap, 6),
        "outbox_gap": outbox_gap,
        "rights_gap": rights_gap,
        "findings_weight": round(findings_weight, 6),
        "identity_gap": round(identity_gap, 6),
    }
    x = sum(components[k] * weights[k] for k in weights)
    return {
        "id": "X",
        "value": round(x, 4),
        "scale": "0=nenhuma incerteza residual operacional; 1=gap total",
        "formula": "sum(component_i * weight_i)",
        "interpretation": (
            "Classificacao B1-B10 esta fechada (control_gap=0). "
            "X e dominado por NOT_RELEASED, recert FAIL, reperformance pendente, "
            "rights e outbox PENDING≠ACK."
        ),
        "components": components,
        "weights": weights,
        "open_counts": {
            "holds": holds,
            "findings_open": findings_open,
            "pending_reperformance": pending_reperf,
            "outbox_pending": outbox_pending,
            "rights_holds": rights_holds,
            "unresolved_identities": unresolved_ids,
            "classified_blocks": classified,
            "released_blocks": released,
        },
    }


def universe() -> dict:
    checkpoints = []
    for block in BLOCKS:
        checkpoints.append(
            {
                "id": block["checkpoint_id"],
                "block": block["id"],
                "result": "PASS_WITH_SCOPED_HOLDS" if block["id"] != "B9" else "PASS_WITH_SCOPED_HOLDS",
                "release": block.get("release", "NOT_APPLICABLE"),
            }
        )
    checkpoints.append(
        {
            "id": "CP-CKO-GLOBAL-FINAL-360-20260902-001",
            "block": "GLOBAL",
            "result": "PASS_WITH_SCOPED_HOLDS",
            "release": "HOLD_NOT_RELEASED",
        }
    )

    folder_rows = [{"path": n, "files": c} for n, c in FOLDERS]
    assert sum(c for _, c in FOLDERS) == 449

    payload = {
        "document": {
            "title": "CKO / CALENF | Relatorio Tecnico Final Controlado",
            "version": "v1.0.0",
            "artifact": "CKO_Relatorio_Tecnico_Final_Controlado_v1.0.0_8142",
            "date": "2026-09-02",
            "classification": "CONTROLLED",
            "robots": "noindex, nofollow",
            "publication": "TECHNICAL_SITE_ONLY",
            "not_production_release": True,
        },
        "baseline": {
            "global_id": "OV-CKO-GLOBAL-FINAL-AUD8L-1.0.0",
            "artifact_id": "ART-CKO-GLOBAL-FINAL-AUD8L-20260902",
            "sha256": GLOBAL_SHA,
            "state": "FINAL_CONTROLLED",
            "checkpoint": "PASS_WITH_SCOPED_HOLDS",
            "release": "HOLD / NOT_RELEASED",
            "master_data": {
                "artifact_id": "ART-CKO-MASTER-DATA-FINAL-CONTROLLED",
                "version_id": "OV-CKO-MASTER-DATA-FINAL-CONTROLLED-1.0.0",
                "state": "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
            },
            "predecessor_44_layers": {
                "artifact_id": "ART-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE",
                "version_id": "OV-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE-1.0.0",
                "state": "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
                "sha256_prefix": "3dd61cd50883",
            },
        },
        "kpis": {
            "blocks_checkpoints": "13/13",
            "aud8l": "104/104",
            "layers": "44/44",
            "layer_x_stage_mesh": "1056/1056",
            "snapshot_files": 449,
            "md_fields": 2496,
            "normative_bindings": 10913,
            "agents_job_profiles": "89/89",
            "aud8l_pass": 91,
            "aud8l_pass_scoped": 13,
            "active_holds": 211,
            "open_findings": 313,
            "learnings": 336,
            "pending_reperformance": 201,
            "snapshot_bytes": 50904695,
            "snapshot_json": 161,
            "snapshot_png": 88,
            "snapshot_html": 66,
            "snapshot_js": 42,
            "snapshot_zip": 42,
            "snapshot_pdf": 10,
        },
        "flow": [
            "MD",
            "REG universal",
            "REG especifico",
            "Schema",
            "Engine",
            "Validator",
            "Renderer",
            "Runtime",
            "AUD-8L",
            "Learning/Reperformance",
            "FINAL_CONTROLLED",
        ],
        "principles": [
            "NO_FACT_WITHOUT_EVIDENCE",
            "discovery != evidence",
            "PENDING != ACK",
            "runtime observado != inferido",
            "release e fail-closed",
        ],
        "finding_cycle": [
            "Finding",
            "Root Cause",
            "Learning",
            "Correction",
            "Regression Test",
            "Reperformance",
            "Recertification",
        ],
        "architecture": [
            "Research Library",
            "Evidence Store",
            "Master Data",
            "Regulatory Graph",
            "Clinical Knowledge",
            "Knowledge Graph",
            "Digital Twin",
            "Agent Job Runtime",
            "Agent Learning",
            "KPACK",
            "CKO Cognitive Runtime",
            "Nurse Intelligence / Nurse-PaLM lineage",
        ],
        "blocks": BLOCKS,
        "lenses": LENSES,
        "checkpoints": checkpoints,
        "priorities": PRIORITIES,
        "drive": DRIVE,
        "inventory": {
            "source": "ALL-SHA256-MANIFEST-20260902.json",
            "scope": "ALL_FILES_MATERIALIZED_IN_CURRENT_EXECUTION_ENVIRONMENT",
            "file_count": 449,
            "hash_algorithm": "SHA-256",
            "bytes": 50904695,
            "folders": folder_rows,
        },
        "supabase": {
            "project_ref": "pgsybzggewhinaniybiy",
            "logical_root": "supabase://pgsybzggewhinaniybiy/cko_governance/controlled_artifacts/",
            "note": "Localizacao logica controlada; nao e arquivo fisico isolado.",
        },
        "limitations": [
            "O PDF documenta a baseline tecnica/controlada do programa. Nao declara release de producao.",
            "O inventario de 449 arquivos e o snapshot materializado do manifesto 2026-09-02, nao uma afirmacao de que todo o Google Drive do usuario esteja contido no pacote.",
            "IDs de Supabase sao localizacoes logicas controladas; nao sao arquivos fisicos isolados.",
            "O conector Google Drive nem sempre expos parent_ids; nesses casos o documento usa Drive ID/URL como localizacao, sem fabricar pasta.",
            "Backup materializado e baseline governada nao equivalem automaticamente a pg_dump/PITR full-restorable com restore test.",
            "Heatmaps sao instrumentos de priorizacao derivados dos estados governados; a evidencia primaria permanece nos checkpoints, findings, holds, versions e hashes.",
        ],
        "unknown_universe": UNKNOWN,
        "residual_uncertainty": residual_uncertainty(),
        "coverage_rules": {
            "coverage": "100% do universo conhecido",
            "evidence_coverage": "100%",
            "test_pass": "100% dos testes definidos",
            "residual_uncertainty": "X",
            "unknown_universe": "explicitado",
        },
        "assurance_stack": [
            "policy-as-code",
            "schemas",
            "graph constraints",
            "CI gates",
            "runtime assertions",
            "automatic evidence",
        ],
        "distributed": {
            "pattern": "EVENT → CHECKPOINT → ORCHESTRATOR",
            "outbox_pending": 296,
            "semantics": "at-least-once with idempotency keys; exactly-once is not claimed",
            "pending_is_not_ack": True,
        },
    }
    return payload


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    uni = universe()
    raw = json.dumps(uni, separators=(",", ":"), ensure_ascii=False, sort_keys=True).encode("utf-8")
    uni["materialization"] = {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "generated_by": "cko-controlled/scripts/generate_universe.py",
        "known_object_count": (
            len(uni["blocks"])
            + len(uni["lenses"])
            + len(uni["checkpoints"])
            + len(uni["priorities"])
            + len(uni["drive"])
            + len(uni["inventory"]["folders"])
            + len(uni["unknown_universe"])
            + len(uni["principles"])
            + len(uni["flow"])
            + len(uni["architecture"])
            + len(uni["limitations"])
            + len(uni["finding_cycle"])
            + len(uni["assurance_stack"])
        ),
    }
    write_json(DATA / "universe.json", uni)
    write_json(DATA / "unknown-universe.json", {"items": UNKNOWN, "rule": "unknown universe = explicitado"})
    write_json(
        DATA / "residual-uncertainty.json",
        uni["residual_uncertainty"],
    )
    print("universe sha256", uni["materialization"]["sha256"])
    print("known objects", uni["materialization"]["known_object_count"])


if __name__ == "__main__":
    main()
