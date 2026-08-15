"""Offline unit tests for the PCI Enfermeiro harvester.

Run with either:
    python scripts/test_harvester.py
    python -m pytest scripts/test_harvester.py
No network access is required.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pci_enfermeiro_harvester as h  # noqa: E402


def test_parse_and_filter():
    rows = h.parse_listing(h.SAMPLE_HTML)
    assert len(rows) == 3
    items = [h.row_to_item(r) for r in rows]
    assert items[0].year == 2026
    assert items[0].scrape_key == "enfermeiro-prefeitura-x-2026"
    matched = [it.scrape_key for it in items if h.item_matches(it, (2025, 2026))]
    assert matched == ["enfermeiro-prefeitura-x-2026"]


def test_classifier():
    hv = h.Harvester.__new__(h.Harvester)
    assert hv._classify("Gabarito Definitivo", "x.pdf")[0] == "final_answer_key_pdf"
    assert hv._classify("Gabarito Preliminar", "x.pdf")[0] == "preliminary_answer_key_pdf"
    assert hv._classify("Gabarito Retificado", "x.pdf")[0] == "rectified_answer_key_pdf"
    assert hv._classify("Prova Objetiva", "prova.pdf")[0] == "exam_pdf"


def test_challenge_detector():
    assert h.looks_like_challenge("... Verificação de segurança ...") is True
    assert h.looks_like_challenge("<html>ok</html>") is False


if __name__ == "__main__":
    raise SystemExit(h.run_selftest())
