"""Data models for markdown chunking."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class DocumentChunk:
    """A labeled markdown chunk passed to extraction agents."""

    chunk_index: int
    section: str
    type: Literal["qa_block", "prose", "prose_chunk", "table_block", "code_block"]
    label: str
    content: str
    has_overlap: bool = False
    char_count: int = field(init=False)

    def __post_init__(self):
        """Populate the computed character count."""
        self.char_count = len(self.content)

    def to_prompt_string(self) -> str:
        """Format chunk as a labeled block for LLM prompt injection."""
        overlap_note = " | overlaps_prev=true" if self.has_overlap else ""
        return (
            f"[CHUNK {self.chunk_index} | Section: {self.section} | "
            f"Type: {self.type} | {self.label}{overlap_note}]\n"
            f"{self.content}\n"
            f"[END CHUNK {self.chunk_index}]"
        )
