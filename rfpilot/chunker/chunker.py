"""Chunk markdown RFP documents into LLM-friendly document chunks."""

import os
import sys

from rfpilot.chunker.chunker_helpers import (
    _chunk_section,
    _load_and_clean_markdown,
    _merge_tiny_chunks,
    _split_into_sections,
)
from rfpilot.chunker.index_builder import build_section_index
from rfpilot.chunker.model import DocumentChunk
from rfpilot.config.constants import PROJECT_ROOT
from rfpilot.exception.exception import RfpilotException
from rfpilot.logging.logger import logging
from rfpilot.utils.file_utils import save_file


# Main Chunker
def smart_rfp_chunker(
    markdown_file: str,
    max_chunk_size: int = 2000,
    min_chunk_size: int = 100,
    qa_group_size: int = 5,
) -> list[DocumentChunk]:
    """
    Multi-strategy chunker for RFP Markdown documents produced by Docling.

    Handles 5 real-world RFP content structures, processed in priority order:
      1. Fenced code blocks  (``` ... ```)          → kept intact, never split
      2. Markdown tables     (| col | col |)         → kept intact as table_block
      3. Numbered Q&A pairs  (1. Q ... Answer: ...)  → grouped by qa_group_size
      4. Large prose         (> max_chunk_size)       → paragraph split with 1-para overlap
      5. Small prose         (<= max_chunk_size)      → single chunk, merged if tiny

    :param:
        markdown_file:   Path to the .md file exported by Docling.
        max_chunk_size:  Max characters per prose chunk before splitting. Default 2000.
        min_chunk_size:  Chunks smaller than this are merged into the previous chunk. Default 100.
        qa_group_size:   Number of Q&A items to group per chunk. Default 5.

    :returns:
        List of DocumentChunk objects, each with a unique chunk_index.

    :raises:
        RfpilotException: Wraps any IO or parsing error with file and section context.
    """
    logging.info(
        "[Chunker] Starting | file='%s' | max_chunk_size=%s | "
        "min_chunk_size=%s | qa_group_size=%s",
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
        if not body:
            logging.debug("[Chunker] Skipping empty section: '%s'", section_title)
            continue

        logging.debug(
            "[Chunker] Processing section: '%s' (%s chars)",
            section_title,
            len(body),
        )

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
                f"[Chunker] Error processing section '{section_title}' "
                f"in '{markdown_file}': {exc}",
                sys,
            ) from exc

        chunks.extend(new_chunks)

    # Post-process: merge orphan tiny chunks into their predecessor
    chunks = _merge_tiny_chunks(chunks, min_chunk_size)

    logging.info(
        "[Chunker] Done | file='%s' | total_chunks=%s",
        markdown_file,
        len(chunks),
    )
    return chunks


if __name__ == "__main__":
    input_file = os.path.join(
        PROJECT_ROOT,
        "output/Dell_Laptop_Specs.md"
    )

    sample_chunks = smart_rfp_chunker(
        markdown_file=input_file,
        max_chunk_size=2000,
        min_chunk_size=100,
        qa_group_size=2,
    )

    SECTION_INDEX = build_section_index(sample_chunks)
    print(SECTION_INDEX)
    print("\n" + "=" * 60 + "\n")

    data = [{chunk.chunk_index: chunk.to_prompt_string()} for chunk in sample_chunks]
    save_file(data, "chunked" + input_file, extension=".json")
