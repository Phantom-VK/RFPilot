"""Generic folder runner for the RFPilot extraction pipeline."""

import json
import sys
from pathlib import Path
from typing import Any

from rfpilot.config.constants import PARSED_ROOT, EXTRACTED_DIR, SUPPORTED_PIPELINE_SUFFIXES
from rfpilot.exception.exception import RfpilotException
from rfpilot.logging.logger import logging
from rfpilot.parser.doc_parser import perform_intelligent_parsing
from rfpilot.pipeline.scatter_gather import process_all_files


def _sort_pipeline_file(file_path: Path) -> tuple[int, str]:
    """Sort likely base RFP files before addendums and supporting documents."""
    name = file_path.name.lower()
    if "addendum" in name:
        return 1, name
    if "final" in name or "rfp" in name:
        return 0, name
    return 2, name


def collect_pipeline_files(input_dir: Path) -> list[Path]:
    """Return supported files directly inside an input directory."""
    if not input_dir.exists():
        raise FileNotFoundError(input_dir)
    if not input_dir.is_dir():
        raise NotADirectoryError(input_dir)

    files = [
        file_path
        for file_path in input_dir.iterdir()
        if (
                file_path.is_file()
                and file_path.suffix.lower() in SUPPORTED_PIPELINE_SUFFIXES
        )
    ]
    return sorted(files, key=_sort_pipeline_file)


def _parsed_output_dir(input_dir: Path) -> Path:
    """Build a stable markdown output folder for source documents."""
    return PARSED_ROOT / input_dir.resolve().name


def parse_sources_to_markdown(files: list[Path], parsed_dir: Path) -> list[Path]:
    """Convert PDF/HTML files to markdown and pass markdown files through."""
    parsed_dir.mkdir(parents=True, exist_ok=True)
    markdown_files: list[Path] = []

    for file_path in files:
        suffix = file_path.suffix.lower()
        if suffix == ".md":
            markdown_files.append(file_path)
            continue

        markdown_file = parsed_dir / f"{file_path.stem}.md"
        if (
            markdown_file.exists()
            and markdown_file.stat().st_mtime >= file_path.stat().st_mtime
        ):
            markdown_files.append(markdown_file)
            logging.info("[Runner] Reusing parsed markdown | file=%s", markdown_file)
            continue

        try:
            markdown = perform_intelligent_parsing(str(file_path))
            markdown_file.write_text(markdown, encoding="utf-8")
            markdown_files.append(markdown_file)
            logging.info("[Runner] Parsed markdown saved | file=%s", markdown_file)
        except (RfpilotException, OSError, ValueError) as exc:
            wrapped_exception = RfpilotException(
                f"[Runner] Failed to parse source document '{file_path}': {exc}",
                sys,
            )
            logging.error(
                "[Runner] Skipping source document | error=%s",
                wrapped_exception,
            )

    return sorted(markdown_files, key=_sort_pipeline_file)


def _output_path(input_dir: Path, markdown_files: list[Path]) -> Path:
    """Choose a result path for the completed extraction."""
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    output_name = (
        markdown_files[0].stem if len(markdown_files) == 1 else input_dir.resolve().name
    )
    return EXTRACTED_DIR / f"{output_name}_result.json"


def save_extraction(
    result: dict[str, Any],
    input_dir: Path,
    markdown_files: list[Path],
) -> Path:
    """Save the final extraction result as JSON."""
    output_path = _output_path(input_dir, markdown_files)
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return output_path


def print_summary(result: dict[str, Any], output_path: Path) -> None:
    """Print a compact extraction summary."""
    extracted_count = sum(value not in (None, "", [], {}) for value in result.values())
    null_count = len(result) - extracted_count
    print(f"Saved extraction output to: {output_path}")
    print(f"Fields extracted: {extracted_count}")
    print(f"Fields null: {null_count}")


async def run_pipeline_for_folder(input_dir: str | Path) -> dict[str, Any]:
    """Run parse, map/reduce, and consolidation for all supported files in a folder."""
    folder = Path(input_dir).expanduser().resolve()
    files = collect_pipeline_files(folder)
    if not files:
        logging.warning("[Runner] No supported files found in %s", folder)
        return {}

    markdown_files = parse_sources_to_markdown(files, _parsed_output_dir(folder))
    if not markdown_files:
        logging.warning("[Runner] No markdown files available for extraction")
        return {}

    markdown_paths = [str(file_path) for file_path in markdown_files]
    logging.info("[Runner] Running pipeline | files=%s", markdown_paths)
    result = await process_all_files(markdown_paths)
    output_path = save_extraction(result, folder, markdown_files)
    print_summary(result, output_path)
    return result
