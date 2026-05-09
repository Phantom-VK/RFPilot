import sys

from rfpilot.chunker.chunker_helpers import (
    _chunk_section,
    _load_and_clean_markdown,
    _merge_tiny_chunks,
    _split_into_sections,
)
from rfpilot.chunker.model import DocumentChunk
from rfpilot.exception.exception import RfpilotException
from rfpilot.logging.logger import logging


def smart_rfp_chunker(
    markdown_file: str,
    max_chunk_size: int = 1200,
    min_chunk_size: int = 120,
    qa_group_size: int = 3,
) -> list[DocumentChunk]:
    logging.info(
        "[Chunker] Starting | file='%s' | max_chunk_size=%s | min_chunk_size=%s | qa_group_size=%s",
        markdown_file,
        max_chunk_size,
        min_chunk_size,
        qa_group_size,
    )

    try:
        markdown = _load_and_clean_markdown(markdown_file)
    except Exception as exc:
        raise RfpilotException(
            f"[Chunker] Failed to read file '{markdown_file}': {exc}", sys
        ) from exc

    sections = _split_into_sections(markdown)
    logging.info("[Chunker] Split into %s heading-based section(s)", len(sections))

    chunks: list[DocumentChunk] = []
    chunk_index = 0

    for section_title, body in sections:
        try:
            new_chunks, chunk_index = _chunk_section(
                body=body,
                section_title=section_title,
                chunk_index=chunk_index,
                max_chunk_size=max_chunk_size,
                qa_group_size=qa_group_size,
            )
        except Exception as exc:
            raise RfpilotException(
                f"[Chunker] Error processing section '{section_title}' in '{markdown_file}': {exc}",
                sys,
            ) from exc

        chunks.extend(new_chunks)

    chunks = _merge_tiny_chunks(chunks, min_chunk_size)

    logging.info(
        "[Chunker] Done | file='%s' | total_chunks=%s",
        markdown_file,
        len(chunks),
    )
    return chunks