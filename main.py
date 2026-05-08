"""Run a focused map/reduce extraction smoke test."""

import asyncio
import json
from pathlib import Path

from rfpilot.agents import merger_agent, structuring_agent
from rfpilot.config.constants import PROJECT_ROOT
from rfpilot.config.settings import settings
from rfpilot.llm.deepseek_client import init_llm
from rfpilot.pipeline.map_reduce import process_single_file

INPUT_FILE = (
    Path(PROJECT_ROOT)
    / "output"
    / "JA-207652 Student and Staff Computing Devices FINAL.md"
)
OUTPUT_DIR = Path(PROJECT_ROOT) / "output" / "map_reduced"


async def run_map_reduce_test() -> dict:
    """Map/reduce the configured sample RFP markdown file."""
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENCY)

    return await process_single_file(
        str(INPUT_FILE),
        structuring_agent,
        merger_agent,
        semaphore,
    )


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    init_llm()
    reduced_result = asyncio.run(run_map_reduce_test())

    output_file_path = OUTPUT_DIR / f"{INPUT_FILE.stem}_map_reduced.json"
    output_file_path.write_text(
        json.dumps(reduced_result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Saved map/reduced output to: {output_file_path}")
