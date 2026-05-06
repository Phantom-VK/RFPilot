from dataclasses import dataclass, field
from typing import Literal


@dataclass
class DocumentChunk:
    chunk_index: int
    section: str
    type: Literal["qa_block", "prose", "prose_chunk", "table_block", "code_block"]
    label: str
    content: str
    has_overlap: bool = False           # True if this chunk shares a paragraph with the previous one
    char_count: int = field(init=False) # Auto-computed — no need to call len() everywhere

    def __post_init__(self):
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
