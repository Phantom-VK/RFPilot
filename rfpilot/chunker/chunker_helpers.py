import logging
import re

from rfpilot.chunker.model import DocumentChunk
from rfpilot.chunker.regex_patterns import _IMAGE_TAG_PATTERN, _HEADING_PATTERN, _TABLE_PATTERN, _QA_SPLIT_PATTERN, \
    _QA_NUM_PATTERN, _CODE_FENCE_PATTERN


def _load_and_clean_markdown(markdown_file: str) -> str:
    """Read the markdown file and strip image placeholder comments."""
    with open(markdown_file, "r", encoding="utf-8") as f:
        content = f.read()
    cleaned = _IMAGE_TAG_PATTERN.sub("", content).strip()
    logging.debug(f"[Chunker] Loaded {len(content)} chars, {len(cleaned)} after cleanup")
    return cleaned


def _split_into_sections(markdown: str) -> list[tuple[str, str]]:
    """
    Split markdown by H1/H2/H3 headings.
    Returns a list of (section_title, body) tuples.
    Any content before the first heading is labeled 'Preamble'.
    """
    raw_sections = _HEADING_PATTERN.split(markdown.strip())
    result = []

    for section in raw_sections:
        section = section.strip()
        if not section:
            continue
        lines = section.splitlines()
        first_line = lines[0] if lines else ""

        if first_line.startswith("#"):
            title = first_line.lstrip("#").strip()
            body = "\n".join(lines[1:]).strip()
        else:
            title = "Preamble"
            body = section

        result.append((title, body))

    return result


def _chunk_section(
    body: str,
    section_title: str,
    chunk_index: int,
    max_chunk_size: int,
    qa_group_size: int,
) -> tuple[list[DocumentChunk], int]:
    """
    Apply the correct chunking strategy to a single section body.
    Priority order:
      1. Code blocks  → extracted and chunked first, remainder processed normally
      2. Table        → single table_block chunk
      3. Q&A          → grouped qa_block chunks
      4. Large prose  → split prose_chunk with overlap
      5. Small prose  → single prose chunk

    :returns list of new chunks, updated chunk_index
    """
    chunks: list[DocumentChunk] = []

    # Extract fenced code blocks first
    # Code blocks must not be split by any other strategy.
    code_blocks, body_without_code = _extract_code_blocks(body)

    if code_blocks:
        logging.debug(
            f"[Chunker] Section '{section_title}': found {len(code_blocks)} code block(s)"
        )
        for i, code in enumerate(code_blocks):
            chunks.append(DocumentChunk(
                chunk_index=chunk_index,
                section=section_title,
                type="code_block",
                label=f"code_{i}",
                content=code,
            ))
            chunk_index += 1

    # Process the rest of the section body
    body = body_without_code.strip()
    if not body:
        return chunks, chunk_index

    # Markdown table
    if "|" in body and _TABLE_PATTERN.search(body):
        logging.debug(f"[Chunker] Section '{section_title}': strategy=table_block")
        chunks.append(DocumentChunk(
            chunk_index=chunk_index,
            section=section_title,
            type="table_block",
            label="table",
            content=body,
        ))
        return chunks, chunk_index + 1

    # Numbered Q&A format
    qa_items = [i.strip() for i in _QA_SPLIT_PATTERN.split(body) if i.strip()]

    if len(qa_items) > 1:
        logging.debug(
            f"[Chunker] Section '{section_title}': strategy=qa_block | "
            f"{len(qa_items)} items, group_size={qa_group_size}"
        )
        for i in range(0, len(qa_items), qa_group_size):
            group = qa_items[i: i + qa_group_size]
            content = "\n\n".join(group)
            q_nums = _QA_NUM_PATTERN.findall("\n".join(group))
            label = f"Q{q_nums[0]}-Q{q_nums[-1]}" if len(q_nums) > 1 else (f"Q{q_nums[0]}" if q_nums else f"group_{i}")

            chunks.append(DocumentChunk(
                chunk_index=chunk_index,
                section=section_title,
                type="qa_block",
                label=label,
                content=content,
            ))
            chunk_index += 1
        return chunks, chunk_index

    # Large prose — paragraph split with 1-paragraph overlap
    if len(body) > max_chunk_size:
        logging.debug(
            f"[Chunker] Section '{section_title}': strategy=prose_chunk | "
            f"{len(body)} chars exceeds limit={max_chunk_size}"
        )
        prose_chunks, chunk_index = _split_large_prose(
            body=body,
            section_title=section_title,
            chunk_index=chunk_index,
            max_chunk_size=max_chunk_size,
        )
        chunks.extend(prose_chunks)
        return chunks, chunk_index

    # Small prose — single chunk
    logging.debug(f"[Chunker] Section '{section_title}': strategy=prose (full, {len(body)} chars)")
    chunks.append(DocumentChunk(
        chunk_index=chunk_index,
        section=section_title,
        type="prose",
        label="full",
        content=body,
    ))
    return chunks, chunk_index + 1


def _extract_code_blocks(body: str) -> tuple[list[str], str]:
    """
    Extract all fenced code blocks (``` ... ```) from the body.
    Returns (list of code block strings, body with code blocks removed).
    """
    code_blocks = _CODE_FENCE_PATTERN.findall(body)
    cleaned_body = _CODE_FENCE_PATTERN.sub("", body)
    return code_blocks, cleaned_body


def _split_large_prose(
    body: str,
    section_title: str,
    chunk_index: int,
    max_chunk_size: int,
) -> tuple[list[DocumentChunk], int]:
    """
    Split a large prose body into chunks by paragraph.
    Applies a 1-paragraph overlap between consecutive chunks for context continuity.
    Uses a local part_index so labels are always part_0, part_1, ... per section.
    """
    paragraphs = re.split(r"\n{2,}", body)
    chunks: list[DocumentChunk] = []
    current: list[str] = []
    current_len = 0
    part_index = 0          # FIX: local counter, not global len(chunks)
    is_overlap_chunk = False

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if current_len + len(para) > max_chunk_size and current:
            chunk_content = "\n\n".join(current)
            chunks.append(DocumentChunk(
                chunk_index=chunk_index,
                section=section_title,
                type="prose_chunk",
                label=f"part_{part_index}",
                content=chunk_content,
                has_overlap=is_overlap_chunk,
            ))
            logging.debug(
                f"[Chunker] prose_chunk part_{part_index} | {len(chunk_content)} chars | "
                f"overlap={is_overlap_chunk}"
            )
            chunk_index += 1
            part_index += 1

            # Keep last paragraph as overlap into the next chunk
            overlap_para = current[-1]
            current = [overlap_para, para]
            current_len = len(overlap_para) + len(para)
            is_overlap_chunk = True  # next chunk carries overlap context
        else:
            current.append(para)
            current_len += len(para)

    # Flush remaining paragraphs
    if current:
        chunk_content = "\n\n".join(current)
        chunks.append(DocumentChunk(
            chunk_index=chunk_index,
            section=section_title,
            type="prose_chunk",
            label=f"part_{part_index}",
            content=chunk_content,
            has_overlap=is_overlap_chunk,
        ))
        logging.debug(
            f"[Chunker] prose_chunk part_{part_index} (final) | {len(chunk_content)} chars"
        )
        chunk_index += 1

    return chunks, chunk_index


def _merge_tiny_chunks(chunks: list[DocumentChunk], min_chunk_size: int) -> list[DocumentChunk]:
    """
    Post-processing step: merge chunks smaller than min_chunk_size into the
    previous chunk. Prevents useless single-line chunks from polluting the index.

    Merged chunks update char_count automatically via __post_init__.
    Code blocks and tables are never merged (they're intentionally standalone).
    """
    if not chunks:
        return chunks

    # qa_block and table_block carry structured meaning — merging them into prose
    # destroys the semantic boundary the LLM relies on for field extraction.
    NEVER_MERGE = {"table_block", "code_block", "qa_block"}
    merged: list[DocumentChunk] = [chunks[0]]

    for current in chunks[1:]:
        prev = merged[-1]

        should_merge = (
            current.char_count < min_chunk_size
            and current.type not in NEVER_MERGE
            and prev.type not in NEVER_MERGE
        )

        if should_merge:
            logging.warning(
                f"[Chunker] Merging tiny chunk [{current.chunk_index}] "
                f"('{current.section}', {current.char_count} chars) "
                f"into chunk [{prev.chunk_index}]"
            )
            merged[-1] = DocumentChunk(
                chunk_index=prev.chunk_index,
                section=prev.section,
                type=prev.type,
                label=prev.label,
                content=prev.content + "\n\n" + current.content,
                has_overlap=prev.has_overlap,
            )
        else:
            merged.append(current)

    # Re-index after merges so chunk_index stays sequential
    for i, chunk in enumerate(merged):
        chunk.chunk_index = i

    if len(merged) < len(chunks):
        logging.info(
            f"[Chunker] Merged {len(chunks) - len(merged)} tiny chunk(s). "
            f"Final count: {len(merged)}"
        )

    return merged
