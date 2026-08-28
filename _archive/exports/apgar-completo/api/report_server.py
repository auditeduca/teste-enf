"""API FastAPI — geração de relatórios HTML a partir de JSON.

Uso:
  pip install -r NIFS/DELIVERY/api/requirements.txt
  uvicorn report_server:app --app-dir NIFS/DELIVERY/api --reload --port 8000

Documentação interativa: http://localhost:8000/docs
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape

from report_models import ReportData

API_DIR = Path(__file__).resolve().parent
DELIVERY_DIR = API_DIR.parent
TEMPLATES_DIR = API_DIR / "templates"

environment = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)

app = FastAPI(
    title="Gerador de Relatórios Clínicos",
    description=(
        "API para gerar relatórios de resultado (Apgar, MEEM e demais ferramentas) "
        "em HTML fiel ao template relatorio-fiel."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory=str(DELIVERY_DIR)), name="assets")


def render_report_html(data: ReportData, *, embed_css: bool = False) -> str:
    css_href = "/assets/css/print-template.css"
    css_inline = ""
    if embed_css:
        css_path = DELIVERY_DIR / "css" / "print-template.css"
        css_inline = css_path.read_text(encoding="utf-8")
        css_href = None

    template = environment.get_template("report_template.html.j2")
    return template.render(
        data=data,
        css_href=css_href,
        css_inline=css_inline,
        ipsg_items=data.resolved_ipsg(),
        med_items=data.resolved_meds(),
        risk_class=data.risk_css_class(),
        show_warning=data.show_warning(),
        show_nnn=bool(
            data.clinical_nnn
            and (data.clinical_nnn.nanda or data.clinical_nnn.nic or data.clinical_nnn.noc)
        ),
        show_meds=data.show_medication_safety and bool(data.resolved_meds()),
    )


@app.get("/health")
async def health():
    return {"status": "ok", "template": "relatorio-fiel"}


@app.get("/schema", summary="Exemplo de payload JSON")
async def schema_example():
    example_path = API_DIR / "report_schema.json"
    if not example_path.is_file():
        raise HTTPException(status_code=404, detail="report_schema.json não encontrado")
    import json

    return JSONResponse(content=json.loads(example_path.read_text(encoding="utf-8")))


@app.post(
    "/generate-report",
    response_class=HTMLResponse,
    summary="Gerar relatório em HTML",
    responses={200: {"content": {"text/html": {}}}},
)
async def generate_report(
    data: ReportData,
    embed_css: bool = Query(False, description="Incorporar CSS no HTML (arquivo standalone)"),
):
    try:
        return HTMLResponse(content=render_report_html(data, embed_css=embed_css))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar o relatório: {exc}") from exc


@app.post("/generate-report/preview", summary="Validar payload e retornar metadados")
async def preview_report(data: ReportData):
    return {
        "valid": True,
        "tool_slug": data.tool_slug,
        "parameter_count": len(data.parameters),
        "risk_level": data.result.risk_level,
        "risk_css_class": data.risk_css_class(),
        "pages": 2,
    }


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return (
        "<h1>API de Geração de Relatórios Clínicos</h1>"
        "<p>POST <code>/generate-report</code> com JSON — veja <a href='/docs'>/docs</a>.</p>"
        "<p>Exemplo de schema: <a href='/schema'>/schema</a></p>"
    )
