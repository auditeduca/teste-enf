from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CONTENT_DIR = ROOT / "datasets" / "master-data" / "content-pending"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
DEFAULT_MODEL = "deepseek-v4-flash"
