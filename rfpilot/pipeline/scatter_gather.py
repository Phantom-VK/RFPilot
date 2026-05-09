"""Scatter/gather pipeline for consolidating extractions across RFP files."""

# pylint: disable=import-error,broad-exception-caught

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

from agents import Runner

from rfpilot.agents import consolidation_agent, merger_agent, structuring_agent
from rfpilot.config.settings import settings
from rfpilot.exception.exception import RfpilotException
from rfpilot.logging.logger import logging
from rfpilot.pipeline.map_reduce import (
    _parse_json_object,
    process_single_file,
)
from rfpilot.schemas.rfp_schema import RFPExtraction


def _strip_source_file(result: dict[str, Any]) -> dict[str, Any]:
    """Remove internal metadata before sending document results to consolidation."""
    cleaned = dict(result)
    cleaned.pop("_source_file", None)
    return cleaned


def _normalize_for_schema(result: dict[str, Any]) -> dict[str, Any]:
    """Normalize common model-output shapes before Pydantic validation."""
    normalized = dict(result)

    contact_info = normalized.get("contact_info")
    if contact_info not in (None, "") and not isinstance(contact_info, dict):
        normalized["contact_info"] = {"raw": str(contact_info)}

    product_specification = normalized.get("product_specification")
    if isinstance(product_specification, list):
        normalized["product_specification"] = "\n".join(
            str(item) for item in product_specification if item not in (None, "")
        )

    return normalized


def _validate_result(result: dict[str, Any]) -> dict[str, Any]:
    """Validate the final extraction and return a JSON-serializable dict."""
    try:
        extraction = RFPExtraction.model_validate(_normalize_for_schema(result))
        return extraction.model_dump(mode="json")
    except Exception as exc:
        raise RfpilotException(
            f"[ScatterGather] Final extraction validation failed: {exc}",
            sys,
        ) from exc


async def _process_file_safely(
    file_path: str,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    """Run map/reduce for one file, returning an empty result on failure."""
    if not Path(file_path).exists():
        logging.warning("[ScatterGather] File not found, skipping | file=%s", file_path)
        return {}

    try:
        return await process_single_file(
            file_path,
            structuring_agent,
            merger_agent,
            semaphore,
        )
    except Exception as exc:
        wrapped_exception = RfpilotException(
            f"[ScatterGather] File processing failed for '{file_path}': {exc}",
            sys,
        )
        logging.error(
            "[ScatterGather] File processing failed | file=%s | error=%s",
            file_path,
            wrapped_exception,
        )
        return {}


async def _consolidate_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Consolidate multiple document-level extractions into one final result."""
    if len(results) == 1:
        logging.info("[ScatterGather] Consolidation skipped | reason=single_file")
        return results[0]

    try:
        result = await asyncio.wait_for(
            Runner.run(
                consolidation_agent,
                input=json.dumps(results),
            ),
            timeout=settings.AGENT_RUN_TIMEOUT_SECONDS,
        )
        return _parse_json_object(result.final_output)
    except Exception as exc:
        wrapped_exception = RfpilotException(
            f"[ScatterGather] Consolidation agent failed: {exc}",
            sys,
        )
        logging.error("[ScatterGather] Consolidation failed | error=%s", wrapped_exception)
        merged = RFPExtraction()
        try:
            for extraction in results:
                merged = RFPExtraction.merge(
                    merged,
                    RFPExtraction.model_validate(_normalize_for_schema(extraction)),
                )
            return merged.model_dump(mode="json")
        except Exception as fallback_exc:
            raise RfpilotException(
                f"[ScatterGather] Local consolidation fallback failed: {fallback_exc}",
                sys,
            ) from fallback_exc


async def process_all_files(file_paths: list[str]) -> dict[str, Any]:
    """Process RFP markdown files in parallel and return the final extraction."""
    start_time = time.perf_counter()
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENCY)
    logging.info("[ScatterGather] Processing files | count=%s", len(file_paths))

    tasks = [
        _process_file_safely(file_path, semaphore)
        for file_path in file_paths
    ]
    per_file_results = await asyncio.gather(*tasks)
    valid_results = [
        _strip_source_file(result)
        for result in per_file_results
        if result
    ]

    if not valid_results:
        logging.warning("[ScatterGather] No valid file results produced")
        return _validate_result({})

    consolidated = await _consolidate_results(valid_results)
    validated = _validate_result(consolidated)
    elapsed = time.perf_counter() - start_time
    logging.info("[ScatterGather] Processing completed | seconds=%.2f", elapsed)
    return validated
