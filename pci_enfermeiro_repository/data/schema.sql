-- Local SQLite checkpoint schema for the PCI Enfermeiro harvester.
-- Mirrors a minimal subset of the Supabase `ingestion` repository so a run can
-- stop/resume offline. Supabase remains the durable repository of record.

CREATE TABLE IF NOT EXISTS runs (
    id            TEXT PRIMARY KEY,
    source_name   TEXT NOT NULL DEFAULT 'pci_concursos',
    target_role   TEXT NOT NULL,
    target_years  TEXT NOT NULL,          -- JSON array, e.g. [2025,2026]
    status        TEXT NOT NULL DEFAULT 'running',
    current_page  INTEGER DEFAULT 0,
    started_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    finished_at   TEXT
);

CREATE TABLE IF NOT EXISTS items (
    scrape_key    TEXT PRIMARY KEY,       -- stable slug from the detail URL
    detail_url    TEXT UNIQUE NOT NULL,
    supabase_id   TEXT,                   -- ingestion.source_catalog_items.id
    title         TEXT,
    role_title    TEXT,
    year          INTEGER,
    institution   TEXT,
    organizer     TEXT,
    access_status TEXT DEFAULT 'discovered',  -- discovered|challenge_required|downloaded
    metadata      TEXT DEFAULT '{}',
    first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_seen_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS artifacts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scrape_key      TEXT NOT NULL,
    artifact_type   TEXT NOT NULL,        -- exam_pdf|answer_key_pdf|final_answer_key_pdf|...
    filename        TEXT NOT NULL,
    source_url      TEXT,
    version_label   TEXT,
    download_status TEXT DEFAULT 'pending',
    sha256          TEXT,
    size_bytes      INTEGER,
    local_path      TEXT,
    UNIQUE (scrape_key, artifact_type, filename)
);
