"""Map/reduce pipeline for extracting structured RFP data from chunks."""

# pylint: disable=import-error,broad-exception-caught

import asyncio
import json
import re
import time
from json import JSONDecodeError
from typing import Any

from agents import Runner

from rfpilot.chunker.chunker import smart_rfp_chunker
from rfpilot.chunker.index_builder import build_section_index
from rfpilot.chunker.model import DocumentChunk
from rfpilot.config.settings import settings
from rfpilot.logging.logger import logging


def _parse_json_object(output: str) -> dict[str, Any]:
    """Parse a JSON object from model output, with a simple substring fallback."""
    try:
        parsed = json.loads(output)
    except JSONDecodeError:
        match = re.search(r"\{.*\}", output, re.DOTALL)
        if not match:
            raise
        parsed = json.loads(match.group(0))

    if not isinstance(parsed, dict):
        logging.warning("[MapReduce] Expected JSON object, got %s", type(parsed).__name__)
        return {}
    return parsed


def _merge_partials_locally(partials: list[dict[str, Any]]) -> dict[str, Any]:
    """Simple fallback merge when the reducer agent does not return valid JSON."""
    merged: dict[str, Any] = {}

    for partial in partials:
        for key, value in partial.items():
            if value in (None, "", [], {}):
                continue

            if key == "product_specification" and key in merged:
                existing = merged[key]
                if isinstance(existing, list):
                    values = existing
                else:
                    values = [existing]

                incoming = value if isinstance(value, list) else [value]
                for item in incoming:
                    if item not in values:
                        values.append(item)
                merged[key] = values
                continue

            merged[key] = value

    return merged


def _chunk_batches(chunks: list[DocumentChunk]) -> list[list[DocumentChunk]]:
    """Group adjacent chunks into small map batches."""
    return [
        chunks[index:index + settings.MAP_CHUNK_BATCH_SIZE]
        for index in range(0, len(chunks), settings.MAP_CHUNK_BATCH_SIZE)
    ]


def _batch_prompt(chunks: list[DocumentChunk]) -> str:
    """Format one or more chunks for a single extraction call."""
    return "\n\n".join(chunk.to_prompt_string() for chunk in chunks)


async def _extract_chunk_batch(
    chunks: list[DocumentChunk],
    structuring_agent: Any,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    """Run the structuring agent for a small chunk batch."""
    async with semaphore:
        batch_start = time.perf_counter()
        chunk_indices = [chunk.chunk_index for chunk in chunks]
        try:
            result = await asyncio.wait_for(
                Runner.run(
                    structuring_agent,
                    input=_batch_prompt(chunks),
                ),
                timeout=settings.AGENT_RUN_TIMEOUT_SECONDS,
            )
            elapsed = time.perf_counter() - batch_start
            logging.info(
                "[MapReduce] Map batch completed | chunk_indices=%s | seconds=%.2f",
                chunk_indices,
                elapsed,
            )
            return _parse_json_object(result.final_output)
        except (JSONDecodeError, Exception) as exc:
            elapsed = time.perf_counter() - batch_start
            logging.warning(
                "[MapReduce] Chunk extraction failed | chunk_indices=%s | seconds=%.2f | error=%s",
                chunk_indices,
                elapsed,
                exc,
            )
            return {}


async def map_phase(
    chunks: list[DocumentChunk],
    structuring_agent: Any,
    semaphore: asyncio.Semaphore | None = None,
) -> list[dict[str, Any]]:
    """Extract partial JSON objects from chunks concurrently."""
    semaphore = semaphore or asyncio.Semaphore(settings.MAX_CONCURRENCY)
    batches = _chunk_batches(chunks)
    logging.info(
        "[MapReduce] Map phase | chunks=%s | batch_size=%s | calls=%s",
        len(chunks),
        settings.MAP_CHUNK_BATCH_SIZE,
        len(batches),
    )
    map_start = time.perf_counter()
    # If only one batch → run it and return directly, skip reduce
    if len(batches) == 1:
        logging.info("[MapReduce] Single batch — skipping reduce phase")
        result = await _extract_chunk_batch(batches[0], structuring_agent, semaphore)
        elapsed = time.perf_counter() - map_start
        logging.info("[MapReduce] Map phase completed | seconds=%.2f", elapsed)
        return [result]
    tasks = [
        _extract_chunk_batch(batch, structuring_agent, semaphore)
        for batch in batches
    ]
    results = await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - map_start
    logging.info("[MapReduce] Map phase completed | seconds=%.2f", elapsed)
    return results


async def reduce_phase(
    partials: list[dict[str, Any]],
    merger_agent: Any,
) -> dict[str, Any]:
    """Merge partial extraction objects into one document-level object."""
    reduce_start = time.perf_counter()
    valid_partials = [partial for partial in partials if partial]
    logging.info(
        "[MapReduce] Reduce phase | partials=%s | valid_partials=%s",
        len(partials),
        len(valid_partials),
    )

    if not valid_partials:
        elapsed = time.perf_counter() - reduce_start
        logging.info("[MapReduce] Reduce phase completed | seconds=%.2f", elapsed)
        return {}
    if len(valid_partials) == 1:
        elapsed = time.perf_counter() - reduce_start
        logging.info(
            "[MapReduce] Reduce phase skipped | reason=single_partial | seconds=%.2f",
            elapsed,
        )
        return valid_partials[0]

    try:
        result = await asyncio.wait_for(
            Runner.run(
                merger_agent,
                input=json.dumps(valid_partials),
            ),
                timeout=settings.AGENT_RUN_TIMEOUT_SECONDS,
            )
        reduced = _parse_json_object(result.final_output)
        elapsed = time.perf_counter() - reduce_start
        logging.info("[MapReduce] Reduce phase completed | seconds=%.2f", elapsed)
        return reduced
    except (JSONDecodeError, Exception) as exc:
        elapsed = time.perf_counter() - reduce_start
        logging.warning("[MapReduce] Reduce phase failed | error=%s", exc)
        logging.info(
            "[MapReduce] Reduce fallback completed | seconds=%.2f",
            elapsed,
        )
        return _merge_partials_locally(valid_partials)


async def process_single_file(
    file_path: str,
    structuring_agent: Any,
    merger_agent: Any,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    """Chunk, map, and reduce one markdown file."""
    file_start = time.perf_counter()
    logging.info("[MapReduce] Processing file | file=%s", file_path)

    chunk_start = time.perf_counter()
    chunks = smart_rfp_chunker(file_path)
    elapsed = time.perf_counter() - chunk_start
    logging.info(
        "[MapReduce] Chunking completed | chunks=%s | seconds=%.2f",
        len(chunks),
        elapsed,
    )
    logging.info("\n%s", build_section_index(chunks))

    partials = await map_phase(chunks, structuring_agent, semaphore)
    reduced = await reduce_phase(partials, merger_agent)
    reduced["_source_file"] = file_path
    elapsed = time.perf_counter() - file_start
    logging.info("[MapReduce] File processing completed | seconds=%.2f", elapsed)
    return reduced
