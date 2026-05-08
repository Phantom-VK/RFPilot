"""Local smoke-test runner for Bid1 scatter/gather extraction."""

import json
import sys
from pathlib import Path
from typing import Any

from rfpilot.config.constants import PROJECT_ROOT
from rfpilot.exception.exception import RfpilotException
from rfpilot.logging.logger import logging
from rfpilot.parser.doc_parser import perform_intelligent_parsing
from rfpilot.pipeline.scatter_gather import process_all_files


BID_DOCS_DIR = Path(PROJECT_ROOT) / "docs" / "test_docs" / "Bid1"
PARSED_DIR = Path(PROJECT_ROOT) / "output" / "parsed" / "Bid1"
EXTRACTED_DIR = Path(PROJECT_ROOT) / "output" / "extracted"
SUPPORTED_SOURCE_SUFFIXES = {".pdf", ".html", ".htm"}


def _sort_bid_file(file_path: Path) -> tuple[int, str]:
    """Sort the base RFP first, then addendums, then any supporting docs."""
    name = file_path.name.lower()
    if "addendum" in name:
        return 1, name
    if "final" in name or "rfp" in name:
        return 0, name
    return 2, name


def _collect_source_documents() -> list[Path]:
    """Return supported source documents for the Bid1 smoke test."""
    if not BID_DOCS_DIR.exists():
        raise FileNotFoundError(BID_DOCS_DIR)

    source_files = [
        file_path
        for file_path in BID_DOCS_DIR.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_SOURCE_SUFFIXES
    ]
    return sorted(source_files, key=_sort_bid_file)


def _parse_documents_to_markdown(source_files: list[Path]) -> list[str]:
    """Parse source PDF/HTML documents into markdown files for extraction."""
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    markdown_files: list[str] = []

    for source_file in source_files:
        markdown_file = PARSED_DIR / f"{source_file.stem}.md"
        if (
            markdown_file.exists()
            and markdown_file.stat().st_mtime >= source_file.stat().st_mtime
        ):
            markdown_files.append(str(markdown_file))
            logging.info("[Bid1Runner] Reusing parsed markdown | file=%s", markdown_file)
            continue

        try:
            markdown = perform_intelligent_parsing(str(source_file))
            markdown_file.write_text(markdown, encoding="utf-8")
            markdown_files.append(str(markdown_file))
            logging.info("[Bid1Runner] Parsed markdown saved | file=%s", markdown_file)
        except (RfpilotException, OSError, ValueError) as exc:
            wrapped_exception = RfpilotException(
                f"[Bid1Runner] Failed to parse source document '{source_file}': {exc}",
                sys,
            )
            logging.error(
                "[Bid1Runner] Skipping source document | error=%s",
                wrapped_exception,
            )

    return sorted(markdown_files, key=lambda file_path: _sort_bid_file(Path(file_path)))


def _save_extraction(result: dict[str, Any], markdown_files: list[str]) -> Path:
    """Save the final scatter/gather extraction result."""
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    base_name = Path(markdown_files[0]).stem if markdown_files else "bid1"
    output_path = EXTRACTED_DIR / f"{base_name}_result.json"
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return output_path


def _print_summary(result: dict[str, Any], output_path: Path) -> None:
    """Print a compact extraction summary."""
    extracted_count = sum(value not in (None, "", [], {}) for value in result.values())
    null_count = len(result) - extracted_count
    print(f"Saved extraction output to: {output_path}")
    print(f"Fields extracted: {extracted_count}")
    print(f"Fields null: {null_count}")


async def run_bid1_scatter_gather_test() -> dict[str, Any]:
    """Parse Bid1 documents and run scatter/gather extraction."""
    source_files = _collect_source_documents()
    if not source_files:
        logging.warning(
            "[Bid1Runner] No supported source documents found in %s",
            BID_DOCS_DIR,
        )
        print(f"No supported source documents found in: {BID_DOCS_DIR}")
        return {}

    markdown_files = _parse_documents_to_markdown(source_files)
    if not markdown_files:
        logging.warning("[Bid1Runner] No markdown files were produced for extraction")
        print("No markdown files were produced for extraction.")
        return {}

    logging.info("[Bid1Runner] Running scatter/gather | files=%s", markdown_files)
    result = await process_all_files(markdown_files)
    output_path = _save_extraction(result, markdown_files)
    _print_summary(result, output_path)
    return result
