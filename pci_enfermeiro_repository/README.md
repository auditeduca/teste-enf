# PCI Enfermeiro Harvester

Internal repository / harvester for public **Enfermeiro** exam papers (2025/2026)
published on [pciconcursos.com.br](https://www.pciconcursos.com.br), feeding the
Supabase `ingestion` factory (`simulados-para-enfermagem`).

It is an internal exam repository, not just a downloader: every discovered exam
page is catalogued with its metadata, and downloaded PDFs are hashed and
registered for the OCR → assembly → DeepSeek → question-factory pipeline.

## How it works

```
PCI listing pages (no CAPTCHA)        PCI detail page (Cloudflare Turnstile)
        │                                        │
        ▼                                        ▼
  parse table rows  ──►  filter 2025/2026   human clears security check ONCE
   (role, year, ...)      + role "Enfermeir"          │
        │                        │                    ▼
        ▼                        ▼             discover PDF links
  local SQLite  ◄────────────────┴──────►  download prova.pdf + gabarito.pdf
   checkpoint                                        │
        │                                            ▼
        ▼                                        SHA-256
  Supabase (cko-pci-harvest-api)  ◄──────────  register_artifact
  ingestion.source_catalog_items / _artifacts
```

### Two phases

1. **Catalog** (`--catalog-only`): crawls the public listing
   `https://www.pciconcursos.com.br/provas/enfermeiro/<page>`, which is **not**
   behind a security check, and records every 2025/2026 Enfermeiro exam page.
   Depends only on the Python standard library.
2. **Download** (default): opens each detail page in a real browser
   (Playwright). Individual PCI download pages are protected by **Cloudflare
   Turnstile**. This tool **never solves or bypasses that challenge** — it waits
   for a human to clear it once, then reuses the browser session to fetch the
   PDFs, hash them (SHA-256), and register them in Supabase.

## Install

```bash
pip install -r requirements.txt
python -m playwright install chromium   # only needed for the download phase
cp config.example.json config.json      # then edit if needed
export INGESTION_WEBHOOK_SECRET=...      # required to write to Supabase
```

The catalog phase runs with no third-party packages and no secret (add
`--no-upload` to keep everything local).

## Usage

```bash
# Offline sanity check (no network):
python scripts/pci_enfermeiro_harvester.py --selftest

# Fill the catalog only (no PDFs, no browser):
python scripts/pci_enfermeiro_harvester.py --config config.json --catalog-only

# Download PDFs (browser opens; you clear the security check):
python scripts/pci_enfermeiro_harvester.py --config config.json

# Resume an interrupted Supabase run:
python scripts/pci_enfermeiro_harvester.py --config config.json \
    --resume-run 20a5d266-999c-417f-8778-6a26c519b6fe

# Local-only (skip Supabase writes):
python scripts/pci_enfermeiro_harvester.py --config config.json --catalog-only --no-upload
```

## Supabase integration

Writes go through the `cko-pci-harvest-api` edge function (actions `start_run`,
`resume_run`, `upsert_item`, `register_artifact`, `finish_run`, `stats`),
authenticated with the `x-ingestion-webhook-secret` header
(`INGESTION_WEBHOOK_SECRET`). Data lands in:

- `ingestion.source_harvest_runs` — one row per run (+ human-in-the-loop columns);
- `ingestion.source_catalog_items` — one row per exam page;
- `ingestion.source_catalog_artifacts` — one row per downloaded PDF (with SHA-256);
- `ingestion.source_harvest_run_items` — run ↔ item link.

## The security check (human-in-the-loop)

Individual PCI download pages show *"Verificação de segurança"* (Cloudflare
Turnstile) before revealing the PDF links. This is an anti-bot control and is
respected, not defeated:

- the crawler stops at the challenge and marks the item `challenge_required`;
- a human clears the check in the visible browser (locally) or in a remote
  Live View (e.g. Browserbase) driven by the panel;
- only then does the harvester read the now-visible PDF links and download them.

Running with `headless: false` (default in `config.example.json`) shows the
browser so a person can clear the check. For a fully virtual flow, point the
download phase at a remote browser with a Live View and surface it in the panel.

## Files

```
pci_enfermeiro_repository/
├── README.md
├── requirements.txt
├── config.example.json
├── scripts/
│   ├── pci_enfermeiro_harvester.py   # crawler + downloader
│   └── test_harvester.py             # offline unit tests
├── data/
│   └── schema.sql                    # SQLite checkpoint schema
└── schemas/
    └── exam_bundle.v1.schema.json    # artifact bundle contract
```
