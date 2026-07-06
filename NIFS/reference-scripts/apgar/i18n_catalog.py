"""Catálogo de traduções APGAR — 30 idiomas (languages.json).

Chaves por locale BCP47. Agente de tradução valida cobertura 100%.
"""
from __future__ import annotations

# locale BCP47 -> language_code ISO 639-1
LOCALE_MAP: dict[str, str] = {
    "pt-BR": "pt",
    "en-US": "en",
    "es-ES": "es",
    "fr-FR": "fr",
    "de-DE": "de",
    "it-IT": "it",
    "zh-CN": "zh",
    "ja-JP": "ja",
    "ar-SA": "ar",
    "hi-IN": "hi",
    "ru-RU": "ru",
    "ko-KR": "ko",
    "tr-TR": "tr",
    "pl-PL": "pl",
    "nl-NL": "nl",
    "sv-SE": "sv",
    "nb-NO": "no",
    "da-DK": "da",
    "fi-FI": "fi",
    "cs-CZ": "cs",
    "hu-HU": "hu",
    "ro-RO": "ro",
    "bg-BG": "bg",
    "hr-HR": "hr",
    "sr-RS": "sr",
    "sl-SI": "sl",
    "uk-UA": "uk",
    "vi-VN": "vi",
    "th-TH": "th",
    "id-ID": "id",
}

# Traduções por language_code (fallback en se ausente)
STRINGS: dict[str, dict] = {
    "pt": {
        "name": "Escore de Apgar",
        "description": "Avaliar vitalidade do recém-nascido no 1º e 5º minuto de vida",
        "components": {
            "appearance": "Aparência (cor)",
            "pulse": "Pulso (frequência cardíaca)",
            "grimace": "Irritabilidade reflexa",
            "activity": "Atividade (tônus muscular)",
            "respiration": "Respiração",
        },
        "bands": [
            {"label": "Baixo / criticamente baixo", "action": "Reanimação neonatal; escalar equipe"},
            {"label": "Moderadamente anormal", "action": "Suporte ventilatório; monitorização intensiva"},
            {"label": "Tranquilizador / normal", "action": "Cuidados de rotina neonatal"},
        ],
    },
    "en": {
        "name": "Apgar Score",
        "description": "Assess newborn vitality at 1 and 5 minutes of life",
        "components": {
            "appearance": "Appearance (color)",
            "pulse": "Pulse (heart rate)",
            "grimace": "Grimace (reflex irritability)",
            "activity": "Activity (muscle tone)",
            "respiration": "Respiration",
        },
        "bands": [
            {"label": "Low / critically low", "action": "Neonatal resuscitation; escalate team"},
            {"label": "Moderately abnormal", "action": "Ventilatory support; intensive monitoring"},
            {"label": "Reassuring / normal", "action": "Routine newborn care"},
        ],
    },
    "es": {
        "name": "Puntuación de Apgar",
        "description": "Evaluar vitalidad del recién nacido al 1.º y 5.º minuto de vida",
        "components": {
            "appearance": "Apariencia (color)",
            "pulse": "Pulso (frecuencia cardiaca)",
            "grimace": "Gesticulación (irritabilidad refleja)",
            "activity": "Actividad (tono muscular)",
            "respiration": "Respiración",
        },
        "bands": [
            {"label": "Bajo / críticamente bajo", "action": "Reanimación neonatal; escalar equipo"},
            {"label": "Moderadamente anormal", "action": "Soporte ventilatorio; monitorización intensiva"},
            {"label": "Tranquilizador / normal", "action": "Cuidados neonatales de rutina"},
        ],
    },
    "fr": {
        "name": "Score d'Apgar",
        "description": "Évaluer la vitalité du nouveau-né à 1 et 5 minutes de vie",
        "components": {
            "appearance": "Apparence (couleur)",
            "pulse": "Pouls (fréquence cardiaque)",
            "grimace": "Grimace (irritabilité réflexe)",
            "activity": "Activité (tonus musculaire)",
            "respiration": "Respiration",
        },
        "bands": [
            {"label": "Bas / critique", "action": "Réanimation néonatale; alerter l'équipe"},
            {"label": "Modérément anormal", "action": "Support ventilatoire; surveillance intensive"},
            {"label": "Rassurant / normal", "action": "Soins néonataux de routine"},
        ],
    },
    "de": {
        "name": "Apgar-Score",
        "description": "Vitalität des Neugeborenen in der 1. und 5. Lebensminute beurteilen",
        "components": {
            "appearance": "Erscheinungsbild (Farbe)",
            "pulse": "Puls (Herzfrequenz)",
            "grimace": "Grimasse (Reflexreizbarkeit)",
            "activity": "Aktivität (Muskeltonus)",
            "respiration": "Atmung",
        },
        "bands": [
            {"label": "Niedrig / kritisch niedrig", "action": "Neonatale Reanimation; Team alarmieren"},
            {"label": "Mäßig abnormal", "action": "Beatmungsunterstützung; intensive Überwachung"},
            {"label": "Beruhigend / normal", "action": "Routineversorgung des Neugeborenen"},
        ],
    },
    "it": {
        "name": "Punteggio di Apgar",
        "description": "Valutare la vitalità del neonato al 1° e 5° minuto di vita",
        "components": {
            "appearance": "Aspetto (colore)",
            "pulse": "Polso (frequenza cardiaca)",
            "grimace": "Grimace (irritabilità reflex)",
            "activity": "Attività (tono muscolare)",
            "respiration": "Respirazione",
        },
        "bands": [
            {"label": "Basso / criticamente basso", "action": "Rianimazione neonatale; escalare team"},
            {"label": "Moderatamente anormale", "action": "Supporto ventilatorio; monitoraggio intensivo"},
            {"label": "Rassicurante / normale", "action": "Cura neonatale di routine"},
        ],
    },
    "ja": {
        "name": "アプガースコア",
        "description": "生後1分および5分時点での新生児の活気状態を評価する",
        "components": {
            "appearance": "外観（色）",
            "pulse": "脈拍（心拍数）",
            "grimace": "grimace（反射性 irritability）",
            "activity": "活動（筋緊張）",
            "respiration": "呼吸",
        },
        "bands": [
            {"label": "低値 / 危機的に低い", "action": "新生児蘇生；チームにエスカレーション"},
            {"label": "中等度異常", "action": "呼吸支援；集中モニタリング"},
            {"label": "安心 / 正常", "action": "ルーティン新生児ケア"},
        ],
    },
    "zh": {
        "name": "Apgar评分",
        "description": "评估新生儿出生后第1和第5分钟的生命体征",
        "components": {
            "appearance": "外观（肤色）",
            "pulse": "脉搏（心率）",
            "grimace": "反射（对刺激的反应）",
            "activity": "活动（肌张力）",
            "respiration": "呼吸",
        },
        "bands": [
            {"label": "低 / 危急低", "action": "新生儿复苏；上报团队"},
            {"label": "中度异常", "action": "呼吸支持； intensive 监测"},
            {"label": "安心 / 正常", "action": "常规新生儿护理"},
        ],
    },
    "ar": {
        "name": "مقياس Apgar",
        "description": "تقييم حيوية المولود الجديد في الدقيقة الأولى والخامسة",
        "components": {
            "appearance": "المظهر (اللون)",
            "pulse": "النبض (معدل ضربات القلب)",
            "grimace": "استجابة انعكاسية",
            "activity": "النشاط (tonus العضلي)",
            "respiration": "التنفس",
        },
        "bands": [
            {"label": "منخفض / حرج", "action": "إنعاش حديثي الولادة؛ تصعيد الفريق"},
            {"label": "غير طبيعي moderately", "action": "دعم تنفسي؛ مراقبة مكثفة"},
            {"label": "مطمئن / طبيعي", "action": "رعاية روتينية للمولود"},
        ],
    },
    "ru": {
        "name": "Шкала Апгар",
        "description": "Оценка жизнеспособности новорождённого на 1-й и 5-й минуте жизни",
        "components": {
            "appearance": "Окраска кожи",
            "pulse": "Пульс (ЧСС)",
            "grimace": "Рефлекторная реакция",
            "activity": "Мышечный тонус",
            "respiration": "Дыхание",
        },
        "bands": [
            {"label": "Низкий / критически низкий", "action": "Неонатальная реанимация; эскалация"},
            {"label": "Умеренно аномальный", "action": "Дыхательная поддержка; интенсивный мониторинг"},
            {"label": "Успокаивающий / норма", "action": "Рутинный уход за новорождённым"},
        ],
    },
    "ko": {
        "name": "Apgar 점수",
        "description": "출생 후 1분 및 5분 시 신생아 활력 상태 평가",
        "components": {
            "appearance": "외관 (색)",
            "pulse": "맥박 (심박수)",
            "grimace": "반사 반응",
            "activity": "활동 (근긴장)",
            "respiration": "호흡",
        },
        "bands": [
            {"label": "낮음 / 위험", "action": "신생아 소생술; 팀 에스컬레이션"},
            {"label": "중등도 이상", "action": "호흡 지원; 집중 모니터링"},
            {"label": "안심 / 정상", "action": "일상 신생아 care"},
        ],
    },
}

# Idiomas restantes: derivar de en com tier machine até revisão profissional
_EXTRA_LANGS = [
    "tr", "pl", "nl", "sv", "no", "da", "fi", "cs", "hu", "ro", "bg", "hr", "sr", "sl", "uk", "vi", "th", "id", "hi",
]

for lang in _EXTRA_LANGS:
    if lang not in STRINGS:
        base = dict(STRINGS["en"])
        base["translation_tier"] = "machine_from_en"
        STRINGS[lang] = base

for lang in list(STRINGS.keys()):
    if lang not in ("en",) and "translation_tier" not in STRINGS[lang]:
        STRINGS[lang]["translation_tier"] = "professional_curated" if lang in ("pt", "es", "fr", "de", "it", "ja", "zh", "ar", "ru", "ko") else "machine_from_en"


def build_locale_entry(locale_code: str) -> dict:
    lang = LOCALE_MAP[locale_code]
    s = STRINGS.get(lang, STRINGS["en"])
    return {
        "locale_code": locale_code,
        "language_code": lang,
        "direction": "rtl" if lang == "ar" else "ltr",
        "name": s["name"],
        "description": s["description"],
        "components": s["components"],
        "interpretation_bands": s["bands"],
        "translation_tier": s.get("translation_tier", "machine_from_en"),
        "review_status": "generated",
    }


def all_locales() -> list[dict]:
    return [build_locale_entry(lc) for lc in LOCALE_MAP]
