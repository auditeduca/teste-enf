"""AI correction suggestions for audit findings (DeepSeek)."""
from __future__ import annotations

from review.deepseek_client import chat_complete

SYSTEM = """Você é consultor de qualidade do repositório CALENF-NKD (Nursing OS).
Dado um achado de auditoria, responda em português com:
1. Causa provável (1 frase)
2. Passos concretos de correção (bullets curtos)
3. Comando ou arquivo a editar, se aplicável
Máximo 120 palavras. Sem markdown code fences."""


def suggest_fix(
    finding: dict,
    *,
    api_key: str,
    model: str = "deepseek-v4-flash",
    report_context: str = "",
) -> str:
    user = (
        f"Framework: {finding.get('framework_id')}\n"
        f"Estágio: {finding.get('stage_id')}\n"
        f"Severidade: {finding.get('severity')}\n"
        f"Código: {finding.get('code')}\n"
        f"Mensagem: {finding.get('message')}\n"
        f"Arquivo: {finding.get('file') or '—'}\n"
    )
    if report_context:
        user += f"\nContexto resumido:\n{report_context[:2000]}\n"
    user += "\nSugira correção prática."

    return chat_complete(
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
        api_key=api_key,
        model=model,
        max_tokens=512,
        temperature=0.3,
    ).strip()
