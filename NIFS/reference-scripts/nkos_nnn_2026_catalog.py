"""NKOS custom NNN catalog generators — reference framework NANDA-I/NIC/NOC 2026."""
from __future__ import annotations

DOMAINS = [
    ("NANDA.DOMAIN.HEALTH_PROMOTION", "Promocao da saude", "CLIN.SAE"),
    ("NANDA.DOMAIN.NUTRITION", "Nutricao", "CLIN.NUTRI"),
    ("NANDA.DOMAIN.ELIMINATION", "Eliminacao e troca", "CLIN.GASTRO"),
    ("NANDA.DOMAIN.ACTIVITY_REST", "Atividade e repouso", "CLIN.REAB"),
    ("NANDA.DOMAIN.PERCEPTION", "Percepcao e cognicao", "CLIN.NEURO"),
    ("NANDA.DOMAIN.SELF_PERCEPTION", "Autopercepcao", "CLIN.PSIQ"),
    ("NANDA.DOMAIN.ROLE", "Relacoes de papel", "CLIN.ENFAM"),
    ("NANDA.DOMAIN.SEXUALITY", "Sexualidade", "CLIN.OBST"),
    ("NANDA.DOMAIN.COPING", "Coping e estresse", "CLIN.SAUDEM"),
    ("NANDA.DOMAIN.LIFE_PRINCIPLES", "Principios da vida", "CLIN.PALIA"),
    ("NANDA.DOMAIN.SAFETY", "Seguranca e protecao", "CLIN.SEGPAC"),
    ("NANDA.DOMAIN.COMFORT", "Conforto", "CLIN.PALIA.DOR"),
    ("NANDA.DOMAIN.GROWTH", "Crescimento e desenvolvimento", "CLIN.PED"),
]

DOMAIN_RANGES = [
    (1, 19), (20, 37), (38, 55), (56, 79), (80, 97), (98, 109), (110, 125),
    (126, 133), (134, 155), (156, 171), (172, 201), (202, 221), (222, 244),
]

CLASSES = [
    "Health awareness", "Health management", "Risk", "Ingestion", "Metabolism",
    "Fluid balance", "Elimination", "Cardiovascular", "Respiratory", "Energy",
    "Sleep", "Self-care", "Abuse", "Neglect", "Communication", "Cognition",
    "Sensation", "Self-concept", "Role", "Relationships", "Sexual function",
    "Stressors", "Coping", "Belief", "Values", "Physical injury", "Violence",
    "Physical comfort", "Environmental", "Growth", "Development",
]

# Curated NKOS 2026 diagnoses (code, en, pt, domain_idx, class, taxonomy, tools, definition)
CURATED_NANDA = {
    "00004": ("Risk for infection", "Risco de infeccao", 10, "Risk", "CLIN.INFCONT", ["TOOL.NEWS2"], "Vulnerabilidade a invasao e multiplicacao de agentes patogenicos."),
    "00007": ("Diarrhea", "Diarreia", 2, "Elimination", "CLIN.GASTRO", [], "Eliminacao de fezes liquidas e aumentadas."),
    "00010": ("Constipation", "Constipacao", 2, "Elimination", "CLIN.GASTRO", [], "Eliminacao intestinal dificil ou infrequente."),
    "00016": ("Activity intolerance", "Intolerancia a atividade", 3, "Energy", "CLIN.REAB", ["TOOL.BARTHEL", "TOOL.KATZ"], "Insuficiencia de energia para completar atividades desejadas."),
    "00030": ("Imbalanced nutrition: less than body requirements", "Nutricao desequilibrada: menos que necessidades", 1, "Ingestion", "CLIN.NUTRI", [], "Ingesta inferior ao metabolismo requerido."),
    "00031": ("Excessive fluid volume", "Volume de liquido excessivo", 1, "Fluid balance", "CLIN.NEFRO", [], "Aumento de liquido isotonico."),
    "00046": ("Impaired gas exchange", "Troca de gases prejudicada", 3, "Respiratory", "CLIN.PNEUMO", ["TOOL.NEWS2", "TOOL.MEWS"], "Deficit na oxigenacao e/ou eliminacao de CO2."),
    "00085": ("Acute pain", "Dor aguda", 11, "Physical comfort", "CLIN.PALIA.DOR", ["TOOL.ESCAL.DOR"], "Experiencia sensorial/emocional desagradavel inicio recente."),
    "00096": ("Death anxiety", "Ansiedade diante da morte", 9, "Belief", "CLIN.PALIA", [], "Sentimento de desconforto por perda da vida humana."),
    "00102": ("Risk for falls", "Risco de quedas", 10, "Risk", "CLIN.SEGPAC.QUED", ["TOOL.MORSE"], "Vulnerabilidade a queda acidental."),
    "00132": ("Chronic pain", "Dor cronica", 11, "Physical comfort", "CLIN.PALIA.DOR", ["TOOL.ESCAL.DOR"], "Dor persistente por mais de 3 meses."),
    "00146": ("Anxiety", "Ansiedade", 8, "Stressors", "CLIN.SAUDEM.ANS", [], "Sentimento de apreensao causado por ameaca real ou imaginaria."),
    "00155": ("Ineffective airway clearance", "Limpeza ineficaz de vias aereas", 3, "Respiratory", "CLIN.PNEUMO", ["TOOL.RASS"], "Incapacidade de limpar secrecoes ou obstrucoes."),
    "00156": ("Fear", "Medo", 8, "Stressors", "CLIN.SAUDEM.ANS", [], "Resposta emocional a ameaca iminente identificada."),
    "00158": ("Fatigue", "Fadiga", 3, "Energy", "CLIN.REAB", [], "Sentimento de cansaco prolongado."),
    "00162": ("Ineffective breathing pattern", "Padrao respiratorio ineficaz", 3, "Respiratory", "CLIN.PNEUMO", ["TOOL.NEWS2"], "Inspiracao/expiracao inadequada."),
    "00194": ("Disturbed sleep pattern", "Padrao de sono perturbado", 3, "Sleep", "CLIN.REAB", [], "Interrupcao do ciclo sono-vigilia."),
    "00198": ("Ineffective health maintenance", "Manutencao ineficaz da saude", 0, "Health management", "CLIN.SAE", [], "Incapacidade de identificar, gerenciar ou procurar atividades de saude."),
    "00202": ("Impaired skin integrity", "Integridade da pele prejudicada", 10, "Physical injury", "CLIN.FERID", ["TOOL.BRADEN"], "Alteracao na epiderme e/ou derme."),
    "00204": ("Impaired tissue integrity", "Integridade tissular prejudicada", 10, "Physical injury", "CLIN.FERID", ["TOOL.BRADEN", "TOOL.WATERLOW"], "Lesao na mucosa ou tecidos correlatos."),
    "00213": ("Risk for deficient fluid volume", "Risco de volume de liquido deficiente", 1, "Risk", "CLIN.NEFRO", [], "Vulnerabilidade a reducao de volume intravascular."),
    "00226": ("Risk for aspiration", "Risco de aspiracao", 10, "Risk", "CLIN.PNEUMO", ["TOOL.GCS"], "Vulnerabilidade a entrada de secrecoes em vias aereas."),
    "00235": ("Risk for impaired skin integrity", "Risco de integridade da pele prejudicada", 10, "Risk", "CLIN.FERID.ULCP", ["TOOL.BRADEN", "TOOL.NORTON", "TOOL.WATERLOW"], "Vulnerabilidade a lesao cutanea."),
}

NIC_DOMAINS = [
    "Physiological", "Complex physiological", "Behavioral", "Family", "Community",
    "Health promotion", "Safety", "Coping", "Physiological", "Complex physiological",
]

NIC_TEMPLATES = [
    ("Assessment", "Avaliacao"), ("Monitoring", "Monitoramento"), ("Management", "Manejo"),
    ("Support", "Suporte"), ("Education", "Educacao"), ("Prevention", "Prevencao"),
    ("Surveillance", "Vigilancia"), ("Therapy", "Terapia"), ("Counseling", "Aconselhamento"),
    ("Coordination", "Coordenacao"), ("Rehabilitation", "Reabilitacao"), ("Comfort", "Conforto"),
    ("Nutrition support", "Suporte nutricional"), ("Medication administration", "Administracao de medicamentos"),
    ("Infection control", "Controle de infeccao"), ("Pain management", "Manejo da dor"),
    ("Fall prevention", "Prevencao de quedas"), ("Airway management", "Manejo de vias aereas"),
    ("Fluid management", "Manejo de liquidos"), ("Wound care", "Cuidados com feridas"),
    ("Skin care", "Cuidados com a pele"), ("Anxiety reduction", "Reducao da ansiedade"),
    ("Sleep enhancement", "Promocao do sono"), ("Family support", "Suporte a familia"),
    ("Health education", "Educacao em saude"), ("Vital signs monitoring", "Monitoramento de sinais vitais"),
    ("Cardiac care", "Cuidados cardiacos"), ("Oxygen therapy", "Oxigenoterapia"),
    ("Positioning", "Posicionamento"), ("Mobility therapy", "Terapia de mobilidade"),
    ("Bowel management", "Manejo intestinal"), ("Urinary care", "Cuidados urinarios"),
    ("Sepsis care", "Cuidados em sepse"), ("Delirium management", "Manejo do delirium"),
    ("Pressure injury prevention", "Prevencao de lesao por pressao"),
]

NOC_DOMAINS = [
    "Physiological", "Functional health", "Psychosocial", "Health knowledge", "Perceived health",
    "Safety", "Family", "Community", "Physiological", "Functional health",
]

NOC_TEMPLATES = [
    ("Status", "Status"), ("Control", "Controle"), ("Level", "Nivel"), ("Behavior", "Comportamento"),
    ("Knowledge", "Conhecimento"), ("Performance", "Desempenho"), ("Tolerance", "Tolerancia"),
    ("Balance", "Balanco"), ("Healing", "Cicatrizacao"), ("Stability", "Estabilidade"),
    ("Comfort", "Conforto"), ("Safety", "Seguranca"), ("Mobility", "Mobilidade"),
    ("Nutrition", "Nutricao"), ("Hydration", "Hidratacao"), ("Elimination", "Eliminacao"),
    ("Breathing", "Respiracao"), ("Circulation", "Circulacao"), ("Consciousness", "Consciencia"),
    ("Pain", "Dor"), ("Sleep", "Sono"), ("Anxiety", "Ansiedade"), ("Coping", "Enfrentamento"),
    ("Infection", "Infeccao"), ("Wound", "Ferida"), ("Skin integrity", "Integridade cutanea"),
    ("Fall prevention", "Prevencao de quedas"), ("Medication compliance", "Aderencia medicamentosa"),
    ("Self-care", "Autocuidado"), ("Quality of life", "Qualidade de vida"),
]

TOOL_DOMAIN_NANDA = {
    "neurology": (4, "Cognition"),
    "wound_care": (10, "Physical injury"),
    "critical_care": (3, "Respiratory"),
    "cardiology": (3, "Cardiovascular"),
    "emergency": (10, "Risk"),
    "geriatrics": (10, "Risk"),
    "pediatrics": (12, "Development"),
    "pharmacology": (10, "Risk"),
    "nutrition": (1, "Ingestion"),
    "mental_health": (8, "Stressors"),
    "respiratory": (3, "Respiratory"),
    "nephrology": (1, "Fluid balance"),
    "infectious_disease": (10, "Risk"),
    "obstetrics": (7, "Sexual function"),
    "pain_management": (11, "Physical comfort"),
    "rehabilitation": (3, "Energy"),
    "safety": (10, "Risk"),
    "assessment_scales": (10, "Risk"),
    "general": (0, "Health management"),
}


def domain_for_code(code: int) -> int:
    for idx, (start, end) in enumerate(DOMAIN_RANGES):
        if start <= code <= end:
            return idx
    return code % len(DOMAINS)


def class_for_code(code: int) -> str:
    return CLASSES[code % len(CLASSES)]


def build_nanda_catalog() -> dict[str, dict]:
    catalog = {}
    for code_str, data in CURATED_NANDA.items():
        en, pt, d_idx, cls, tax, tools, defn = data
        catalog[code_str] = {
            "name": en, "name_pt": pt,
            "domain_code": DOMAINS[d_idx][0], "class_code": f"NANDA.CLASS.{cls.upper().replace(' ', '_')}",
            "taxonomy_code": tax, "related_tool_codes": tools, "definition": defn,
        }
    for i in range(1, 245):
        code = f"{i:05d}"
        if code in catalog:
            continue
        d_idx = domain_for_code(i)
        domain_code, domain_pt, default_tax = DOMAINS[d_idx]
        cls = class_for_code(i)
        seq = (i - DOMAIN_RANGES[d_idx][0]) + 1
        en = f"{cls} alteration pattern {seq}"
        pt = f"Padrao alterado de {cls.lower()} {seq} ({domain_pt.lower()})"
        catalog[code] = {
            "name": en, "name_pt": pt,
            "domain_code": domain_code,
            "class_code": f"NANDA.CLASS.{cls.upper().replace(' ', '_')}",
            "taxonomy_code": default_tax,
            "related_tool_codes": [],
            "definition": f"Diagnostico NKOS 2026 customizado vinculado a {domain_pt.lower()}.",
        }
    return catalog


# Real clinical tool codes for NIC curation (not taxonomy buckets TOOL.CALC/ESCAL/PROTO).
NIC_CURATED_TOOL_CODES: dict[str, list[str]] = {
    "1040": ["TOOL.9RIGHTS"],
    "1100": ["TOOL.GCS", "TOOL.RASS"],
    "1120": ["TOOL.BRADEN", "TOOL.NORTON"],
    "1340": ["TOOL.INFUSION", "TOOL.INSULIN", "TOOL.9RIGHTS"],
    "1450": ["TOOL.MORSE"],
    "1860": ["TOOL.BRADEN", "TOOL.NORTON", "TOOL.WATERLOW"],
    "2300": ["TOOL.NEWS2", "TOOL.MEWS", "TOOL.SOFA"],
    "2380": ["TOOL.RASS", "TOOL.CAM-ICU"],
    "2410": ["TOOL.SOFA", "TOOL.APACHE2"],
    "2500": ["TOOL.PARKLAND", "TOOL.BMI"],
    "2800": ["TOOL.NRS2002", "TOOL.BMI"],
    "3010": ["TOOL.GCS"],
    "3110": ["TOOL.RASS"],
    "3310": ["TOOL.GCS"],
    "3540": ["TOOL.BRADEN", "TOOL.WATERLOW"],
}

_TOOL_BUCKET_TYPES: dict[str, tuple[str, ...]] = {
    "TOOL.CALC": (
        "dose_calculation", "anthropometric", "fluid_balance", "nutritional",
        "renal", "hemodynamic", "pediatric", "custom",
    ),
    "TOOL.ESCAL": ("score", "risk_stratification", "neurological", "respiratory"),
    "TOOL.PROTO": ("protocol",),
}

_INVALID_TOOL_BUCKETS = frozenset({"TOOL.CALC", "TOOL.ESCAL", "TOOL.PROTO"})


def tool_codes_for_bucket(bucket: str, tools: list[dict]) -> list[str]:
    types = _TOOL_BUCKET_TYPES.get(bucket, ())
    return [t["tool_code"] for t in tools if t.get("tool_type") in types]


def resolve_nic_tool_codes(nic_code: str, bucket_or_codes: list[str], tools: list[dict]) -> list[str]:
    """Map NIC to real catalog tool_code values."""
    if nic_code in NIC_CURATED_TOOL_CODES:
        return list(NIC_CURATED_TOOL_CODES[nic_code])
    bucket = bucket_or_codes[0] if len(bucket_or_codes) == 1 and bucket_or_codes[0] in _INVALID_TOOL_BUCKETS else ""
    if bucket:
        pool = tool_codes_for_bucket(bucket, tools)
        if pool:
            return [pool[int(nic_code) % len(pool)]]
    valid = [c for c in bucket_or_codes if c not in _INVALID_TOOL_BUCKETS]
    return valid


def build_nic_catalog(codes: list[str], tools: list[dict] | None = None) -> dict[str, dict]:
    catalog = {}
    curated = {
        "1040": ("Infection control", "Controle de infeccao", "Safety", ["Higiene de maos", "Barreiras"]),
        "1100": ("Pain management", "Manejo da dor", "Physiological", ["Avaliar dor", "Analgesia"]),
        "1120": ("Positioning", "Posicionamento", "Physiological", ["Mudanca de decubito"]),
        "1340": ("Medication administration", "Administracao de medicamentos", "Safety", ["Checagem 9 certos"]),
        "1450": ("Fall prevention", "Prevencao de quedas", "Safety", ["Campainha", "Calcado antiderrapante"]),
        "1860": ("Skin surveillance", "Vigilancia da pele", "Physiological", ["Inspecao cutanea"]),
        "2300": ("Vital signs monitoring", "Monitoramento de sinais vitais", "Physiological", ["PA", "FC", "FR", "SpO2"]),
        "2380": ("Airway management", "Manejo de vias aereas", "Physiological", ["Aspiracao", "Oxigenio"]),
        "2410": ("Oxygen therapy", "Oxigenoterapia", "Physiological", ["Cateter nasal", "Mascara"]),
        "2500": ("Fluid management", "Manejo de liquidos", "Physiological", ["Balanco hidrico"]),
        "2800": ("Nutrition management", "Manejo nutricional", "Physiological", ["Dieta", "Suplementacao"]),
        "3010": ("Anxiety reduction", "Reducao da ansiedade", "Coping", ["Presenca terapeutica"]),
        "3110": ("Sleep enhancement", "Promocao do sono", "Coping", ["Rotina", "Ambiente"]),
        "3310": ("Health education", "Educacao em saude", "Health promotion", ["Orientacao"]),
        "3540": ("Wound care", "Cuidados com feridas", "Physiological", ["Curativo", "Limpeza"]),
    }
    for code in codes:
        if code in curated:
            en, pt, dom, acts = curated[code]
            entry = {"name": en, "name_pt": pt, "domain": dom, "activities": acts,
                     "definition": f"Intervencao NKOS 2026: {pt.lower()}."}
            if tools and code in NIC_CURATED_TOOL_CODES:
                entry["related_tool_codes"] = list(NIC_CURATED_TOOL_CODES[code])
            catalog[code] = entry
        else:
            tpl = NIC_TEMPLATES[int(code) % len(NIC_TEMPLATES)]
            dom = NIC_DOMAINS[int(code) % len(NIC_DOMAINS)]
            focus = ["TOOL.CALC", "TOOL.ESCAL", "TOOL.PROTO"][int(code) % 3]
            tax = {"Physiological": "CLIN.UTI", "Safety": "CLIN.SEGPAC", "Coping": "CLIN.SAUDEM",
                   "Health promotion": "CLIN.SAE", "Family": "CLIN.ENFAM"}.get(dom, "CLIN.SAE")
            related = resolve_nic_tool_codes(code, [focus], tools or []) if tools else [focus]
            catalog[code] = {
                "name": f"{tpl[0]} procedure {code}",
                "name_pt": f"{tpl[1]} procedimento {code}",
                "domain": dom, "activities": [f"Executar {tpl[1].lower()}"],
                "definition": f"Intervencao NIC NKOS 2026 customizada ({dom.lower()}).",
                "taxonomy_code": tax, "related_tool_codes": related,
            }
    return catalog


def build_noc_catalog(codes: list[str]) -> dict[str, dict]:
    catalog = {}
    curated = {
        "0200": ("Pain control", "Controle da dor", "Physiological", ["Escala numerica", "Comportamento"]),
        "0301": ("Knowledge: disease process", "Conhecimento: processo de doenca", "Health knowledge", ["Explicacao"]),
        "0400": ("Risk control", "Controle de risco", "Safety", ["Identificacao de riscos"]),
        "0708": ("Infection status", "Status de infeccao", "Physiological", ["Sinais flogisticos"]),
        "1100": ("Sleep", "Sono", "Functional health", ["Horas dormidas"]),
        "1602": ("Fall prevention behavior", "Comportamento de prevencao de quedas", "Safety", ["Uso de dispositivos"]),
        "1902": ("Wound healing", "Cicatrizacao de feridas", "Physiological", ["Granulacao"]),
        "2102": ("Nutritional status", "Status nutricional", "Physiological", ["IMC", "Albumina"]),
        "2300": ("Fluid balance", "Balanco hidrico", "Physiological", ["Diurese"]),
    }
    for code in codes:
        if code in curated:
            en, pt, dom, ind = curated[code]
            catalog[code] = {"name": en, "name_pt": pt, "domain": dom, "indicators": ind,
                             "definition": f"Desfecho NKOS 2026: {pt.lower()}."}
        else:
            tpl = NOC_TEMPLATES[int(code) % len(NOC_TEMPLATES)]
            dom = NOC_DOMAINS[int(code) % len(NOC_DOMAINS)]
            catalog[code] = {
                "name": f"{tpl[0]} outcome {code}",
                "name_pt": f"Desfecho de {tpl[1].lower()} {code}",
                "domain": dom,
                "indicators": [f"Indicador de {tpl[1].lower()}"],
                "definition": f"Desfecho NOC NKOS 2026 customizado ({dom.lower()}).",
            }
    return catalog


def tool_nanda_links(tools: list[dict], nanda_by_tax: dict[str, list[str]]) -> dict[str, list[str]]:
    links = {}
    for t in tools:
        domain = t.get("domain", "general")
        d_idx, cls = TOOL_DOMAIN_NANDA.get(domain, TOOL_DOMAIN_NANDA["general"])
        tax = DOMAINS[d_idx][2]
        candidates = nanda_by_tax.get(tax, [])
        if not candidates:
            candidates = [f"NANDA.{c:05d}" for c in range(DOMAIN_RANGES[d_idx][0], DOMAIN_RANGES[d_idx][1] + 1)]
        links[t["tool_code"]] = candidates[:3]
    curated_tools = {
        "TOOL.MORSE": ["NANDA.00102"], "TOOL.BRADEN": ["NANDA.00235", "NANDA.00202"], "TOOL.NORTON": ["NANDA.00235"],
        "TOOL.WATERLOW": ["NANDA.00235"], "TOOL.GCS": ["NANDA.00226", "NANDA.00155"],
        "TOOL.RASS": ["NANDA.00155"], "TOOL.CAM-ICU": ["NANDA.00155"],
        "TOOL.NEWS2": ["NANDA.00046", "NANDA.00004"], "TOOL.MEWS": ["NANDA.00046"],
        "TOOL.BARTHEL": ["NANDA.00016"], "TOOL.KATZ": ["NANDA.00016"],
        "TOOL.APACHE2": ["NANDA.00046"], "TOOL.SOFA": ["NANDA.00046"],
        "TOOL.qSOFA": ["NANDA.00004"],
    }
    links.update(curated_tools)
    return links
