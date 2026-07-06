"""Gera DDL Supabase (Postgres + JSONB)."""
from __future__ import annotations

from config import all_entities
from paths import SCHEMA_OUT


def generate_supabase_ddl() -> str:
    lines = [
        "-- NKOS Database Sync — schema Supabase/Postgres",
        "-- Gerado automaticamente por database_sync_agents",
        "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
        "",
        "CREATE TABLE IF NOT EXISTS nkos_sync_runs (",
        "  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),",
        "  run_id TEXT NOT NULL,",
        "  target TEXT NOT NULL,",
        "  status TEXT NOT NULL,",
        "  entities JSONB,",
        "  summary JSONB,",
        "  created_at TIMESTAMPTZ DEFAULT NOW()",
        ");",
        "",
    ]

    for meta in all_entities():
        table = meta["table"]
        lines.extend([
            f"CREATE TABLE IF NOT EXISTS {table} (",
            "  id UUID PRIMARY KEY,",
            "  entity_key TEXT NOT NULL,",
            "  business_key TEXT NOT NULL,",
            "  country_code TEXT,",
            "  locale_code TEXT,",
            "  schema_version TEXT,",
            "  payload JSONB NOT NULL,",
            "  synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),",
            "  UNIQUE (entity_key, business_key)",
            ");",
            f"CREATE INDEX IF NOT EXISTS idx_{table}_country ON {table}(country_code);",
            f"CREATE INDEX IF NOT EXISTS idx_{table}_locale ON {table}(locale_code);",
            f"CREATE INDEX IF NOT EXISTS idx_{table}_payload ON {table} USING GIN (payload);",
            "",
        ])

    return "\n".join(lines)


def write_schema_file() -> str:
    SCHEMA_OUT.parent.mkdir(parents=True, exist_ok=True)
    ddl = generate_supabase_ddl()
    SCHEMA_OUT.write_text(ddl + "\n", encoding="utf-8")
    return str(SCHEMA_OUT)
