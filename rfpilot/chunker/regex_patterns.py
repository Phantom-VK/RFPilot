"""Compiled regular expressions used by the markdown chunker."""

import re

_HEADING_PATTERN   = re.compile(r"(?=^#{1,3} .+)", re.MULTILINE)
_QA_SPLIT_PATTERN  = re.compile(r"(?=^\d+[.)]\s+\S)", re.MULTILINE)
_QA_NUM_PATTERN    = re.compile(r"^(\d+)[.)]", re.MULTILINE)
_TABLE_PATTERN     = re.compile(r"\|.+\|.+\|")
_IMAGE_TAG_PATTERN = re.compile(r"<!--\s*image\s*-->", re.IGNORECASE)
_CODE_FENCE_PATTERN = re.compile(r"(```[\s\S]*?```)", re.MULTILINE)
