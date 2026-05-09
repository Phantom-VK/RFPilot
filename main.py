"""Run the RFPilot extraction pipeline for a folder of RFP files."""

import argparse
import asyncio
from pathlib import Path

from rfpilot.llm.deepseek_client import init_llm
from rfpilot.runners.pipeline_runner import run_pipeline_for_folder


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Run the RFPilot pipeline on a folder of .md, .pdf, or .html files."
        ),
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Folder containing the files to process.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    # Disabled the commandline arguments temporary
    # args = _parse_args()
    init_llm()
    input_dir = "docs/test_docs/Bid1"
    asyncio.run(run_pipeline_for_folder(input_dir))
