import asyncio

from agents import Runner

from rfpilot.agents.test_agent import test_agent
from rfpilot.llm.deepseek_client import init_llm


async def run_agent(query:str):
    result = await Runner.run(
        starting_agent=test_agent,
        input=f"Query:{query}"
    )
    print(result.final_output)


if __name__ == "__main__":
    init_llm()
    asyncio.run(run_agent("Hello there"))
