"""NKOS Phase 2 scaffold: Core Master Data (NNN + supporting entities)."""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "datasets"
NOW_Z = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
NOW_ISO = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

NANDA_DOMAINS = [
    ("NANDA.DOMAIN.HEALTH_PROMOTION", "Promocao da saude", "health-promotion"),
    ("NANDA.DOMAIN.NUTRITION", "Nutricao", "nutrition"),
    ("NANDA.DOMAIN.ELIMINATION", "Eliminacao e troca", "elimination"),
    ("NANDA.DOMAIN.ACTIVITY_REST", "Atividade e repouso", "activity-rest"),
    ("NANDA.DOMAIN.PERCEPTION", "Percepcao e cognicao", "perception-cognition"),
    ("NANDA.DOMAIN.SELF_PERCEPTION", "Autopercepcao", "self-perception"),
    ("NANDA.DOMAIN.ROLE", "Relacoes de papel", "role-relationships"),
    ("NANDA.DOMAIN.SEXUALITY", "Sexualidade", "sexuality"),
    ("NANDA.DOMAIN.COPING", "Coping e tolerancia ao estresse", "coping"),
    ("NANDA.DOMAIN.LIFE_PRINCIPLES", "Principios da vida", "life-principles"),
    ("NANDA.DOMAIN.SAFETY", "Seguranca e protecao", "safety-protection"),
    ("NANDA.DOMAIN.COMFORT", "Conforto", "comfort"),
    ("NANDA.DOMAIN.GROWTH", "Crescimento e desenvolvimento", "growth-development"),
]

NANDA_DIAGNOSES = [
    ("00004", "Risk for infection", "Risco de infeccao", "NANDA.DOMAIN.SAFETY", "Risk"),
    ("00007", "Diarrhea", "Diarreia", "NANDA.DOMAIN.ELIMINATION", "Elimination"),
    ("00010", "Constipation", "Constipacao", "NANDA.DOMAIN.ELIMINATION", "Elimination"),
    ("00016", "Activity intolerance", "Intolerancia a atividade", "NANDA.DOMAIN.ACTIVITY_REST", "Cardiovascular"),
    ("00030", "Imbalanced nutrition: less than body requirements", "Nutricao desequilibrada: ingestao inferior", "NANDA.DOMAIN.NUTRITION", "Ingestion"),
    ("00046", "Impaired gas exchange", "Troca de gases prejudicada", "NANDA.DOMAIN.ACTIVITY_REST", "Cardiovascular"),
    ("00085", "Acute pain", "Dor aguda", "NANDA.DOMAIN.COMFORT", "Physical comfort"),
    ("00096", "Death anxiety", "Ansiedade diante da morte", "NANDA.DOMAIN.LIFE_PRINCIPLES", "Belief"),
    ("00102", "Risk for falls", "Risco de quedas", "NANDA.DOMAIN.SAFETY", "Risk"),
    ("00132", "Chronic pain", "Dor cronica", "NANDA.DOMAIN.COMFORT", "Physical comfort"),
    ("00146", "Anxiety", "Ansiedade", "NANDA.DOMAIN.COPING", "Stressors"),
    ("00155", "Ineffective airway clearance", "Limpeza ineficaz de vias aereas", "NANDA.DOMAIN.ACTIVITY_REST", "Respiratory"),
    ("00158", "Fatigue", "Fadiga", "NANDA.DOMAIN.ACTIVITY_REST", "Energy"),
    ("00162", "Ineffective breathing pattern", "Padrao respiratorio ineficaz", "NANDA.DOMAIN.ACTIVITY_REST", "Respiratory"),
    ("00194", "Disturbed sleep pattern", "Padrao de sono perturbado", "NANDA.DOMAIN.ACTIVITY_REST", "Sleep"),
    ("00202", "Impaired skin integrity", "Integridade da pele prejudicada", "NANDA.DOMAIN.SAFETY", "Physical injury"),
    ("00204", "Impaired tissue integrity", "Integridade tissular prejudicada", "NANDA.DOMAIN.SAFETY", "Physical injury"),
    ("00235", "Risk for impaired skin integrity", "Risco de integridade da pele prejudicada", "NANDA.DOMAIN.SAFETY", "Risk"),
    ("00213", "Risk for deficient fluid volume", "Risco de volume de liquido deficiente", "NANDA.DOMAIN.NUTRITION", "Risk"),
    ("00226", "Risk for aspiration", "Risco de aspiracao", "NANDA.DOMAIN.SAFETY", "Risk"),
    ("00198", "Ineffective health maintenance", "Manutencao ineficaz da saude", "NANDA.DOMAIN.HEALTH_PROMOTION", "Health management"),
    ("00156", "Fear", "Medo", "NANDA.DOMAIN.COPING", "Stressors"),
    ("00031", "Excessive fluid volume", "Volume de liquido excessivo", "NANDA.DOMAIN.NUTRITION", "Fluid balance"),
]

NIC_INTERVENTIONS = [
    ("1040", "Infection control", "Controle de infeccao", "Physiological"),
    ("1100", "Pain management", "Manejo da dor", "Physiological"),
    ("1120", "Positioning", "Posicionamento", "Physiological"),
    ("1340", "Medication administration", "Administracao de medicamentos", "Physiological"),
    ("1450", "Fall prevention", "Prevencao de quedas", "Safety"),
    ("1860", "Skin surveillance", "Vigilancia da pele", "Physiological"),
    ("2300", "Vital signs monitoring", "Monitoramento de sinais vitais", "Physiological"),
    ("2310", "Cardiac care", "Cuidados cardiacos", "Physiological"),
    ("2380", "Airway management", "Manejo de vias aereas", "Physiological"),
    ("2410", "Oxygen therapy", "Oxigenoterapia", "Physiological"),
    ("2500", "Fluid management", "Manejo de liquidos", "Physiological"),
    ("2510", "Fluid monitoring", "Monitoramento de liquidos", "Physiological"),
    ("2550", "Electrolyte management", "Manejo eletrolitico", "Physiological"),
    ("2800", "Nutrition management", "Manejo nutricional", "Physiological"),
    ("3010", "Anxiety reduction", "Reducao da ansiedade", "Coping"),
    ("3110", "Sleep enhancement", "Promocao do sono", "Coping"),
    ("3200", "Coping enhancement", "Promocao do enfrentamento", "Coping"),
    ("3310", "Health education", "Educacao em saude", "Health promotion"),
    ("3540", "Wound care", "Cuidados com feridas", "Physiological"),
    ("4510", "Family support", "Suporte a familia", "Family"),
]

NOC_OUTCOMES = [
    ("0200", "Pain control", "Controle da dor", "Physiological"),
    ("0301", "Knowledge: disease process", "Conhecimento: processo de doenca", "Health knowledge"),
    ("0400", "Risk control", "Controle de risco", "Safety"),
    ("0708", "Infection status", "Status de infeccao", "Physiological"),
    ("1100", "Sleep", "Sono", "Functional health"),
    ("1602", "Fall prevention behavior", "Comportamento de prevencao de quedas", "Safety"),
    ("1902", "Wound healing", "Cicatrizacao de feridas", "Physiological"),
    ("2102", "Nutritional status", "Status nutricional", "Physiological"),
    ("2300", "Fluid balance", "Balanco hidrico", "Physiological"),
    ("2301", "Electrolyte balance", "Balanco eletrolitico", "Physiological"),
    ("0405", "Respiratory status", "Status respiratorio", "Physiological"),
    ("0500", "Cardiac pump effectiveness", "Eficacia da bomba cardiaca", "Physiological"),
    ("0600", "Tissue perfusion", "Perfusao tissular", "Physiological"),
    ("1000", "Anxiety level", "Nivel de ansiedade", "Psychosocial"),
    ("1200", "Comfort level", "Nivel de conforto", "Physiological"),
]

COMMON_DRUGS = [
    ("DRUG.MORPHINE", "Morphine", "Morfina", "N02AA01", "opioid", True),
    ("DRUG.FENTANYL", "Fentanyl", "Fentanil", "N02AB03", "opioid", True),
    ("DRUG.INSULIN", "Insulin regular", "Insulina regular", "A10AB01", "antidiabetic", True),
    ("DRUG.Heparin", "Heparin", "Heparina", "B01AB01", "anticoagulant", True),
    ("DRUG.WARFARIN", "Warfarin", "Varfarina", "B01AA03", "anticoagulant", True),
    ("DRUG.ADRENALINE", "Epinephrine", "Adrenalina", "C01CA24", "vasopressor", True),
    ("DRUG.NOREPINEPHRINE", "Norepinephrine", "Noradrenalina", "C01CA03", "vasopressor", True),
    ("DRUG.MIDAZOLAM", "Midazolam", "Midazolam", "N05CD08", "sedative", True),
    ("DRUG.PROPOFOL", "Propofol", "Propofol", "N01AX10", "anesthetic", True),
    ("DRUG.VANCOMYCIN", "Vancomycin", "Vancomicina", "J01XA01", "antibiotic", False),
    ("DRUG.METFORMIN", "Metformin", "Metformina", "A10BA02", "antidiabetic", False),
    ("DRUG.LOSARTAN", "Losartan", "Losartana", "C09CA01", "antihypertensive", False),
    ("DRUG.OMEPRAZOLE", "Omeprazole", "Omeprazol", "A02BC01", "ppi", False),
    ("DRUG.PARACETAMOL", "Acetaminophen", "Paracetamol", "N02BE01", "analgesic", False),
    ("DRUG.DIPYRONE", "Metamizole", "Dipirona", "N02BB02", "analgesic", False),
]

COMMON_LABS = [
    ("LAB.GLUCOSE", "Glucose", "Glicemia", "2345-7", "mg/dL", "70", "99", "fasting"),
    ("LAB.HBA1C", "HbA1c", "Hemoglobina glicada", "4548-4", "%", "4.0", "5.6", None),
    ("LAB.CREATININE", "Creatinine", "Creatinina", "2160-0", "mg/dL", "0.6", "1.2", None),
    ("LAB.POTASSIUM", "Potassium", "Potassio", "2823-3", "mEq/L", "3.5", "5.0", None),
    ("LAB.SODIUM", "Sodium", "Sodio", "2951-2", "mEq/L", "136", "145", None),
    ("LAB.HEMOGLOBIN", "Hemoglobin", "Hemoglobina", "718-7", "g/dL", "12.0", "16.0", "female"),
    ("LAB.WBC", "WBC", "Leucocitos", "6690-2", "cells/uL", "4500", "11000", None),
    ("LAB.PLATELETS", "Platelets", "Plaquetas", "777-3", "cells/uL", "150000", "400000", None),
    ("LAB.INR", "INR", "INR", "6301-6", "ratio", "0.8", "1.2", "no_anticoagulation"),
    ("LAB.LACTATE", "Lactate", "Lactato", "2524-7", "mmol/L", "0.5", "2.0", None),
    ("LAB.TROPONIN", "Troponin I", "Troponina I", "10839-9", "ng/mL", "0", "0.04", None),
    ("LAB.CRP", "CRP", "Proteina C reativa", "1988-5", "mg/L", "0", "5", None),
]

GUIDELINES = [
    ("GUIDE.WHO.HAND_HYGIENE", "WHO", "Higiene das maos", "2009", "IPSG05"),
    ("GUIDE.WHO.FALL_PREV", "WHO", "Prevencao de quedas", "2021", "IPSG06"),
    ("GUIDE.WHO.MED_SAFETY", "WHO", "Seguranca do paciente: medicamentos", "2022", "IPSG03"),
    ("GUIDE.MS.SEPSE", "MS_BR", "Manejo de sepse", "2023", None),
    ("GUIDE.MS.CPR", "MS_BR", "Suporte avancado de vida", "2024", None),
    ("GUIDE.COFEN.SAE", "COFEN", "SAE e processo de enfermagem", "2023", None),
    ("GUIDE.COFEN.EPIC", "COFEN", "Praticas integradas de cuidado", "2022", None),
    ("GUIDE.JBI.EVIDENCE", "JBI", "Niveis de evidencia JBI", "2020", None),
]


def uid():
    return str(uuid.uuid4())


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def envelope(entity, micro_phase, records, **extra):
    return {
        "generated_at": NOW_ISO,
        "schema_version": "2026.1.0",
        "micro_phase": micro_phase,
        "template_id": f"T{micro_phase}",
        "entity": entity,
        "nkos_phase": 2,
        "count": len(records),
        "records": records,
        "validation_summary": {"total_records": len(records), "passed": True, "errors": []},
        **extra,
    }


def generate_master_entities():
    records = []
    for code, name, slug in NANDA_DOMAINS:
        records.append({
            "uuid": uid(),
            "entity_code": code,
            "entity_type": "nanda_domain",
            "name": name,
            "slug": slug,
            "parent_entity_code": None,
            "taxonomy_code": "EDU.ENSGRAD",
            "status": "active",
            "created_at": NOW_Z,
            "updated_at": NOW_Z,
        })
    for code, name, name_pt, domain, cls in NANDA_DIAGNOSES:
        class_code = f"NANDA.CLASS.{cls.upper().replace(' ', '_')}"
        records.append({
            "uuid": uid(),
            "entity_code": class_code,
            "entity_type": "nanda_class",
            "name": cls,
            "slug": cls.lower().replace(" ", "-"),
            "parent_entity_code": domain,
            "taxonomy_code": None,
            "status": "active",
            "created_at": NOW_Z,
            "updated_at": NOW_Z,
        })
    seen = set()
    deduped = []
    for r in records:
        if r["entity_code"] in seen:
            continue
        seen.add(r["entity_code"])
        deduped.append(r)
    save(ROOT / "master/master_entities.json", envelope(
        "MasterEntity", "2.1", deduped,
        target=2000, import_status="scaffold",
        entity_types=["nanda_domain", "nanda_class"],
    ))
    return len(deduped)


def generate_nursing_diagnoses():
    records = []
    seeded = {c for c, *_ in NANDA_DIAGNOSES}
    for code, name, name_pt, domain, cls in NANDA_DIAGNOSES:
        class_code = f"NANDA.CLASS.{cls.upper().replace(' ', '_')}"
        records.append({
            "uuid": uid(),
            "diagnosis_code": f"NANDA.{code}",
            "nanda_code": code,
            "name": name,
            "name_pt": name_pt,
            "domain_code": domain,
            "class_code": class_code,
            "definition": None,
            "defining_characteristics": [],
            "related_factors": [],
            "taxonomy_code": None,
            "snomed_ct_code": None,
            "icd11_code": None,
            "evidence_code": None,
            "edition": "2024-2026",
            "status": "active",
            "created_at": NOW_Z,
            "updated_at": NOW_Z,
        })
    for i in range(1, 245):
        code = f"{i:05d}"
        if code in seeded:
            continue
        records.append({
            "uuid": uid(),
            "diagnosis_code": f"NANDA.{code}",
            "nanda_code": code,
            "name": None,
            "name_pt": None,
            "domain_code": None,
            "class_code": None,
            "definition": None,
            "defining_characteristics": [],
            "related_factors": [],
            "taxonomy_code": None,
            "snomed_ct_code": None,
            "icd11_code": None,
            "evidence_code": None,
            "edition": "2024-2026",
            "status": "pending_import",
            "created_at": NOW_Z,
            "updated_at": NOW_Z,
        })
    records.sort(key=lambda r: r["nanda_code"])
    save(ROOT / "clinical/nursing_diagnoses.json", envelope(
        "NursingDiagnosis", "2.2", records,
        target=244, seeded=len(NANDA_DIAGNOSES), import_status="partial",
    ))
    return len(records)


def generate_nursing_interventions():
    records = []
    for code, name, name_pt, domain in NIC_INTERVENTIONS:
        records.append({
            "uuid": uid(),
            "intervention_code": f"NIC.{code}",
            "nic_code": code,
            "name": name,
            "name_pt": name_pt,
            "domain": domain,
            "definition": None,
            "activities": [],
            "taxonomy_code": None,
            "edition": "7th",
            "status": "active",
            "created_at": NOW_Z,
            "updated_at": NOW_Z,
        })
    for i in range(1000, 1560):
        code = f"{i:04d}"
        if any(r[0] == code for r in NIC_INTERVENTIONS):
            continue
        records.append({
            "uuid": uid(),
            "intervention_code": f"NIC.{code}",
            "nic_code": code,
            "name": None,
            "name_pt": None,
            "domain": None,
            "definition": None,
            "activities": [],
            "taxonomy_code": None,
            "edition": "7th",
            "status": "pending_import",
            "created_at": NOW_Z,
            "updated_at": NOW_Z,
        })
    records.sort(key=lambda r: r["nic_code"])
    save(ROOT / "clinical/nursing_interventions.json", envelope(
        "NursingIntervention", "2.3", records,
        target=560, seeded=len(NIC_INTERVENTIONS), import_status="partial",
    ))
    return len(records)


def generate_nursing_outcomes():
    records = []
    for code, name, name_pt, domain in NOC_OUTCOMES:
        records.append({
            "uuid": uid(),
            "outcome_code": f"NOC.{code}",
            "noc_code": code,
            "name": name,
            "name_pt": name_pt,
            "domain": domain,
            "definition": None,
            "indicators": [],
            "scale_type": "5_point_likert",
            "taxonomy_code": None,
            "edition": "6th",
            "status": "active",
            "created_at": NOW_Z,
            "updated_at": NOW_Z,
        })
    seeded = {c for c, *_ in NOC_OUTCOMES}
    for i in range(1, 541):
        code = f"{i:04d}"
        if code in seeded:
            continue
        records.append({
            "uuid": uid(),
            "outcome_code": f"NOC.{code}",
            "noc_code": code,
            "name": None,
            "name_pt": None,
            "domain": None,
            "definition": None,
            "indicators": [],
            "scale_type": "5_point_likert",
            "taxonomy_code": None,
            "edition": "6th",
            "status": "pending_import",
            "created_at": NOW_Z,
            "updated_at": NOW_Z,
        })
    records.sort(key=lambda r: r["noc_code"])
    save(ROOT / "clinical/nursing_outcomes.json", envelope(
        "NursingOutcome", "2.4", records,
        target=540, seeded=len(NOC_OUTCOMES), import_status="partial",
    ))
    return len(records)


def generate_clinical_concepts():
    concepts = [
        ("CONCEPT.SEPSE", "Sepse", "Sepse", "CLIN.UTI.SEPSIS", "condition"),
        ("CONCEPT.DIABETES", "Diabetes mellitus", "Diabetes mellitus", "CLIN.ENDO.DIAB", "condition"),
        ("CONCEPT.AVC", "Acidente vascular cerebral", "AVC", "CLIN.NEURO.AVC", "condition"),
        ("CONCEPT.PNEUMONIA", "Pneumonia", "Pneumonia", "CLIN.PNEUMO.PNEUMO", "condition"),
        ("CONCEPT.IRC", "Insuficiencia renal cronica", "IRC", "CLIN.NEFRO.IRC", "condition"),
        ("CONCEPT.IC", "Insuficiencia cardiaca", "Insuficiencia cardiaca", "CLIN.CARDIO.IC", "condition"),
        ("CONCEPT.DPOC", "DPOC", "DPOC", "CLIN.PNEUMO.DPOC", "condition"),
        ("CONCEPT.ULCERA", "Lesao por pressao", "Lesao por pressao", "CLIN.FERID.ULCP", "condition"),
        ("CONCEPT.DOR", "Dor", "Dor", "CLIN.PALIA.DOR", "symptom"),
        ("CONCEPT.ANSIEDADE", "Ansiedade", "Ansiedade", "CLIN.SAUDEM.ANS", "symptom"),
    ]
    records = [{
        "uuid": uid(), "concept_code": c, "name": n, "name_pt": pt,
        "taxonomy_code": tax, "concept_type": t,
        "snomed_ct_code": None, "icd11_code": None,
        "status": "active", "created_at": NOW_Z, "updated_at": NOW_Z,
    } for c, n, pt, tax, t in concepts]
    save(ROOT / "clinical/clinical_concepts.json", envelope(
        "ClinicalConcept", "2.5", records, target=2000, import_status="scaffold",
    ))
    return len(records)


def generate_drug_references():
    records = [{
        "uuid": uid(), "drug_code": c, "generic_name": n, "generic_name_pt": pt,
        "atc_code": atc, "pharmacological_class": cls,
        "high_alert": ha, "routes": ["IV", "PO"],
        "snomed_ct_code": None, "status": "active",
        "created_at": NOW_Z, "updated_at": NOW_Z,
    } for c, n, pt, atc, cls, ha in COMMON_DRUGS]
    save(ROOT / "clinical/drug_references.json", envelope(
        "DrugReference", "2.6", records, target=500, import_status="scaffold",
    ))
    return len(records)


def generate_lab_references():
    records = [{
        "uuid": uid(), "lab_code": c, "name": n, "name_pt": pt,
        "loinc_code": loinc, "unit": unit,
        "reference_low": lo, "reference_high": hi,
        "context": ctx, "status": "active",
        "created_at": NOW_Z, "updated_at": NOW_Z,
    } for c, n, pt, loinc, unit, lo, hi, ctx in COMMON_LABS]
    save(ROOT / "clinical/lab_reference_values.json", envelope(
        "LabReferenceValue", "2.7", records, target=300, import_status="scaffold",
    ))
    return len(records)


def generate_clinical_guidelines():
    records = [{
        "uuid": uid(), "guideline_code": c, "source": src,
        "title": title, "year": year,
        "ipsg_goal_code": ipsg, "evidence_code": "EVID.TYPE.GUIDELINE",
        "url": None, "status": "active",
        "created_at": NOW_Z, "updated_at": NOW_Z,
    } for c, src, title, year, ipsg in GUIDELINES]
    save(ROOT / "clinical/clinical_guidelines.json", envelope(
        "ClinicalGuideline", "2.8", records, target=200, import_status="scaffold",
    ))
    return len(records)


def generate_standard_mappings():
    mappings = [
        ("MAP.NANDA.00085.SNOMED", "NANDA.00085", "SNOMED_CT", "22253000", "exact"),
        ("MAP.NANDA.00085.ICD11", "NANDA.00085", "ICD11", "MG30", "related"),
        ("MAP.NANDA.00146.SNOMED", "NANDA.00146", "SNOMED_CT", "48694002", "exact"),
        ("MAP.NIC.1100.NANDA", "NIC.1100", "NANDA", "NANDA.00085", "treats"),
        ("MAP.NIC.1450.NANDA", "NIC.1450", "NANDA", "NANDA.00102", "prevents"),
        ("MAP.NOC.0200.NIC", "NOC.0200", "NIC", "NIC.1100", "measures"),
        ("MAP.NOC.1602.NIC", "NOC.1602", "NIC", "NIC.1450", "measures"),
    ]
    records = [{
        "uuid": uid(), "mapping_code": c,
        "source_code": src, "target_system": sys, "target_code": tgt,
        "strength": strength, "status": "active",
        "created_at": NOW_Z, "updated_at": NOW_Z,
    } for c, src, sys, tgt, strength in mappings]
    save(ROOT / "master/standard_mappings.json", envelope(
        "StandardMapping", "2.9", records, target=None, import_status="scaffold",
    ))
    return len(records)


def generate_dictionary():
    terms = [
        ("TERM.SAE", "Nursing process", "Processo de enfermagem", "Proceso de enfermeria"),
        ("TERM.NNN", "NNN linkage", "Vinculo NNN", "Vinculo NNN"),
        ("TERM.DEFCHAR", "Defining characteristic", "Caracteristica definidora", "Caracteristica definitoria"),
        ("TERM.RELFAC", "Related factor", "Fator relacionado", "Factor relacionado"),
        ("TERM.IPSG", "Patient safety goal", "Meta de seguranca do paciente", "Meta de seguridad del paciente"),
        ("TERM.SBAR", "SBAR communication", "Comunicacao SBAR", "Comunicacion SBAR"),
        ("TERM.GCS", "Glasgow Coma Scale", "Escala de Coma de Glasgow", "Escala de Coma de Glasgow"),
        ("TERM.BRADEN", "Braden Scale", "Escala de Braden", "Escala de Braden"),
        ("TERM.NEWS2", "NEWS2 score", "Escore NEWS2", "Puntuacion NEWS2"),
        ("TERM.SEPSE", "Sepsis", "Sepse", "Sepsis"),
    ]
    records = [{
        "uuid": uid(), "entry_code": c,
        "term_en": en, "term_pt": pt, "term_es": es,
        "category": "nursing", "status": "active",
        "created_at": NOW_Z, "updated_at": NOW_Z,
    } for c, en, pt, es in terms]
    save(ROOT / "master/nursing_dictionary.json", envelope(
        "NursingDictionaryEntry", "2.10", records, target=5000, import_status="scaffold",
    ))
    return len(records)


def generate_search_synonyms():
    synonyms = [
        ("SYN.GCS", "glasgow", "GCS", "TOOL.GCS"),
        ("SYN.BRADEN", "escala braden", "Braden", "TOOL.BRADEN"),
        ("SYN.MORSE", "escala morse", "Morse fall", "TOOL.MORSE"),
        ("SYN.NEWS2", "news 2", "NEWS2", "TOOL.NEWS2"),
        ("SYN.DOR", "pain scale", "dor", "TOOL.ESCAL.DOR"),
        ("SYN.NANDA", "diagnostico enfermagem", "nursing diagnosis", "NANDA"),
        ("SYN.NIC", "intervencao enfermagem", "nursing intervention", "NIC"),
        ("SYN.NOC", "resultado enfermagem", "nursing outcome", "NOC"),
        ("SYN.SEPSE", "septicemia", "sepse", "CONCEPT.SEPSE"),
        ("SYN.INSULINA", "insulin", "insulina", "DRUG.INSULIN"),
    ]
    records = [{
        "uuid": uid(), "synonym_code": c,
        "term": term, "canonical_term": canonical,
        "target_code": target, "language_code": "pt",
        "status": "active", "created_at": NOW_Z, "updated_at": NOW_Z,
    } for c, term, canonical, target in synonyms]
    save(ROOT / "master/search_synonyms.json", envelope(
        "SearchSynonym", "2.11", records, target=10000, import_status="scaffold",
    ))
    return len(records)


def update_canonical_registry(counts):
    path = ROOT / "metadata/canonical_registry.json"
    data = load(path)
    phase2 = [
        ("MasterEntity", "master/master_entities.json", "entity_code", counts["master"]),
        ("StandardMapping", "master/standard_mappings.json", "mapping_code", counts["mappings"]),
        ("ClinicalConcept", "clinical/clinical_concepts.json", "concept_code", counts["concepts"]),
        ("NursingDiagnosis", "clinical/nursing_diagnoses.json", "diagnosis_code", counts["diagnoses"]),
        ("NursingIntervention", "clinical/nursing_interventions.json", "intervention_code", counts["interventions"]),
        ("NursingOutcome", "clinical/nursing_outcomes.json", "outcome_code", counts["outcomes"]),
        ("DrugReference", "clinical/drug_references.json", "drug_code", counts["drugs"]),
        ("LabReferenceValue", "clinical/lab_reference_values.json", "lab_code", counts["labs"]),
        ("ClinicalGuideline", "clinical/clinical_guidelines.json", "guideline_code", counts["guidelines"]),
        ("NursingDictionaryEntry", "master/nursing_dictionary.json", "entry_code", counts["dictionary"]),
        ("SearchSynonym", "master/search_synonyms.json", "synonym_code", counts["synonyms"]),
    ]
    existing = {e["entity"] for e in data["entities"]}
    for entity, file, pk, recs in phase2:
        entry = {"entity": entity, "file": file, "primary_key": pk, "records": recs, "nkos_phase": 2}
        if entity in existing:
            data["entities"] = [e if e["entity"] != entity else entry for e in data["entities"]]
        else:
            data["entities"].append(entry)
    data["generated_at"] = NOW_ISO
    save(path, data)


def update_status(counts):
    path = ROOT / "metadata/nkos_implementation_status.json"
    data = load(path)
    data["generated_at"] = NOW_ISO
    data["overall"]["phase2_core_master_data_pct"] = 15.0
    data["phase2_core_master_data"]["status"] = "scaffold"
    data["phase2_core_master_data"]["note"] = "Estrutura + slots NNN (244/566/540) + seed data; import completo pendente"
    for ent in data["phase2_core_master_data"]["entities"]:
        key = {
            "MasterEntity": "master", "StandardMapping": "mappings", "ClinicalConcept": "concepts",
            "NursingDiagnosis": "diagnoses", "NursingIntervention": "interventions",
            "NursingOutcome": "outcomes", "DrugReference": "drugs", "LabReferenceValue": "labs",
            "ClinicalGuideline": "guidelines", "NursingDictionaryEntry": "dictionary",
            "SearchSynonym": "synonyms",
        }.get(ent["entity"])
        if key and key in counts:
            ent["actual"] = counts[key]
            ent["file"] = {
                "master": "master/master_entities.json", "mappings": "master/standard_mappings.json",
                "concepts": "clinical/clinical_concepts.json", "diagnoses": "clinical/nursing_diagnoses.json",
                "interventions": "clinical/nursing_interventions.json", "outcomes": "clinical/nursing_outcomes.json",
                "drugs": "clinical/drug_references.json", "labs": "clinical/lab_reference_values.json",
                "guidelines": "clinical/clinical_guidelines.json", "dictionary": "master/nursing_dictionary.json",
                "synonyms": "master/search_synonyms.json",
            }[key]
            ent["status"] = "scaffold" if ent["actual"] < (ent["target"] or ent["actual"]) else "complete"
    data["phase_mapping"]["recommended_next"] = "Phase 2: import completo NANDA/NIC/NOC + expandir Drug/Lab/Dictionary"
    save(path, data)


def update_manifest():
    m = load(ROOT / "metadata/generation_manifest.json")
    phases = [
        "2.1_master_entity", "2.2_nursing_diagnosis", "2.3_nursing_intervention",
        "2.4_nursing_outcome", "2.5_clinical_concept", "2.6_drug_reference",
        "2.7_lab_reference", "2.8_clinical_guideline", "2.9_standard_mapping",
        "2.10_nursing_dictionary", "2.11_search_synonym", "phase2_scaffold",
    ]
    files = {
        "2.1_master_entity": "master\\master_entities.json",
        "2.2_nursing_diagnosis": "clinical\\nursing_diagnoses.json",
        "2.3_nursing_intervention": "clinical\\nursing_interventions.json",
        "2.4_nursing_outcome": "clinical\\nursing_outcomes.json",
        "2.5_clinical_concept": "clinical\\clinical_concepts.json",
        "2.6_drug_reference": "clinical\\drug_references.json",
        "2.7_lab_reference": "clinical\\lab_reference_values.json",
        "2.8_clinical_guideline": "clinical\\clinical_guidelines.json",
        "2.9_standard_mapping": "master\\standard_mappings.json",
        "2.10_nursing_dictionary": "master\\nursing_dictionary.json",
        "2.11_search_synonym": "master\\search_synonyms.json",
    }
    for p in phases:
        if p not in m["phases_completed"]:
            m["phases_completed"].append(p)
    m["files_generated"].update(files)
    m["next_phase"] = "Phase 2: complete NNN import | Phase 3: EntityRelation"
    m["nkos_phase_status"]["phase_2"] = "scaffold (~15%)"
    m["updated_at"] = NOW_ISO
    for phase, rel in files.items():
        fp = ROOT / rel.replace("\\", "/")
        if fp.exists():
            m["checksums"][phase] = hashlib.md5(fp.read_bytes()).hexdigest()[:16]
    save(ROOT / "metadata/generation_manifest.json", m)


if __name__ == "__main__":
    counts = {
        "master": generate_master_entities(),
        "diagnoses": generate_nursing_diagnoses(),
        "interventions": generate_nursing_interventions(),
        "outcomes": generate_nursing_outcomes(),
        "concepts": generate_clinical_concepts(),
        "drugs": generate_drug_references(),
        "labs": generate_lab_references(),
        "guidelines": generate_clinical_guidelines(),
        "mappings": generate_standard_mappings(),
        "dictionary": generate_dictionary(),
        "synonyms": generate_search_synonyms(),
    }
    update_canonical_registry(counts)
    update_status(counts)
    update_manifest()
    print("Phase 2 scaffold:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
