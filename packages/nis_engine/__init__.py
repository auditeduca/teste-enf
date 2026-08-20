"""NIS engine — validate, score, and generate clinical calculator pages."""

from .score import compute, interpret, score_of
from .validate import load_schema, validate_tool, validate_tools_dir
from .generate import generate_index, generate_tool_page

__all__ = [
    "compute",
    "interpret",
    "score_of",
    "load_schema",
    "validate_tool",
    "validate_tools_dir",
    "generate_index",
    "generate_tool_page",
]

__version__ = "0.1.0"
