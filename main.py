"""Run an end-to-end scatter/gather extraction smoke test for Bid1."""

import asyncio

from rfpilot.llm.deepseek_client import init_llm
from rfpilot.runners.bid1_scatter_gather import run_bid1_scatter_gather_test


if __name__ == "__main__":
    init_llm()
    asyncio.run(run_bid1_scatter_gather_test())
