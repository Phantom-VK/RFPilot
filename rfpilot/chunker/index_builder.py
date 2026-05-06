"""Build lightweight indexes for generated document chunks."""

import logging

from rfpilot.chunker.model import DocumentChunk


def build_section_index(chunks: list[DocumentChunk]) -> str:
    """
    Builds a lightweight section map string for the Orchestrator Agent.
    The agent reads this first to navigate, then requests specific chunks by index.

    Example output:
        Document Section Index (8 chunks):
          [0] Preamble → prose (full) — 420 chars
          [1] Bid Terms → qa_block (Q1-Q5) — 980 chars
          [2] Bid Terms → qa_block (Q6-Q8) — 540 chars
          [3] Technical Specs → table_block (table) — 1200 chars
    """
    logging.info("[Chunker] Building section index for %s chunk(s)", len(chunks))
    lines = [f"Document Section Index ({len(chunks)} chunks):"]
    for c in chunks:
        overlap_tag = " [+overlap]" if c.has_overlap else ""
        lines.append(
            f"  [{c.chunk_index}] {c.section} → {c.type} "
            f"({c.label}){overlap_tag} — {c.char_count} chars"
        )
    return "\n".join(lines)
