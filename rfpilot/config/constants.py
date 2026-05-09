"""Project-wide constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
PARSED_ROOT = Path(PROJECT_ROOT) / "output" / "parsed"
EXTRACTED_DIR = Path(PROJECT_ROOT) / "output" / "extracted"
SUPPORTED_SOURCE_SUFFIXES = {".pdf", ".html", ".htm"}
SUPPORTED_PIPELINE_SUFFIXES = SUPPORTED_SOURCE_SUFFIXES | {".md"}
