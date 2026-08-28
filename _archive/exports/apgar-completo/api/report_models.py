"""Modelos Pydantic para geração de relatórios clínicos (todas as ferramentas)."""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

RiskLevel = Literal["none", "low", "moderate", "high", "critical", "unknown"]

DEFAULT_IPSG = [
    {"tag": "M1", "text": "Identificar o paciente corretamente"},
    {"tag": "M2", "text": "Melhorar a comunicação efetiva"},
    {"tag": "M3", "text": "Segurança na prescrição e administração"},
    {"tag": "M5", "text": "Higiene das mãos"},
    {"tag": "M6", "text": "Reduzir o risco de quedas"},
]

DEFAULT_MEDS = [
    "Paciente certo",
    "Medicamento certo",
    "Via certa",
    "Hora certa",
    "Dose certa",
    "Registro certo",
    "Ação certa",
    "Forma certa",
    "Resposta certa",
]


class ReportInfo(BaseModel):
    title: str = "Relatório de Resultado"
    date: str
    time: str
    exam_name: str
    exam_description: str = ""
    logo_url: Optional[str] = None


class Patient(BaseModel):
    name: str = "—"
    reg: str = "—"
    age: str = "—"
    bed: str = "—"
    # aliases usados em integrações externas (MEEM / Manus)
    id: Optional[str] = Field(default=None, validation_alias="id")
    location: Optional[str] = None

    @model_validator(mode="after")
    def merge_aliases(self) -> "Patient":
        if self.reg == "—" and self.id:
            self.reg = self.id
        if self.bed == "—" and self.location:
            self.bed = self.location
        return self


class Parameter(BaseModel):
    label: str
    score: str


class Result(BaseModel):
    score: str | int | float
    total: Optional[int] = None
    unit: str = "pontos"
    classification: str
    risk_level: RiskLevel = "unknown"
    show_warning_icon: Optional[bool] = None


class ClinicalNnn(BaseModel):
    nanda: Optional[str] = None
    nic: Optional[str] = None
    noc: Optional[str] = None


class SafetyItem(BaseModel):
    tag: Optional[str] = None
    text: str


class Responsible(BaseModel):
    name: str = "Enf. Responsável"
    id: str = "COREN: _______"


class ReportData(BaseModel):
    """Payload genérico — compatível com Apgar, MEEM e demais calculadoras."""

    report_info: ReportInfo
    patient: Patient = Field(default_factory=Patient)
    parameters: List[Parameter] = Field(default_factory=list)
    result: Result
    clinical_interpretation: str = ""
    clinical_nnn: Optional[ClinicalNnn] = None
    safety_ipsg: Optional[List[SafetyItem]] = None
    safety_meds: Optional[List[str]] = None
    show_medication_safety: bool = True
    reference: Optional[str] = None
    responsible: Responsible = Field(default_factory=Responsible)
    tool_slug: Optional[str] = None

    def resolved_ipsg(self) -> List[SafetyItem]:
        if self.safety_ipsg:
            return self.safety_ipsg
        return [SafetyItem(**item) for item in DEFAULT_IPSG]

    def resolved_meds(self) -> List[str]:
        if self.safety_meds:
            return self.safety_meds
        return list(DEFAULT_MEDS)

    def risk_css_class(self) -> str:
        level = self.result.risk_level
        if level in ("critical", "high"):
            return "rr-risk--critical"
        if level == "moderate":
            return "rr-risk--moderate"
        if level in ("none", "low"):
            return "rr-risk--none"
        return "rr-risk--moderate"

    def show_warning(self) -> bool:
        if self.result.show_warning_icon is not None:
            return self.result.show_warning_icon
        return self.result.risk_level in ("moderate", "high", "critical")
