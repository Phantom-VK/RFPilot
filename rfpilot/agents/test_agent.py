from agents import Agent

from rfpilot.config.settings import settings
from rfpilot.prompts.agent_instructions import TEST_AGENT_INSTRTUCTIONS

test_agent = Agent(
        name="Test agent",
        instructions=TEST_AGENT_INSTRTUCTIONS,
        model=settings.DEEPSEEK_MODEL,
    )