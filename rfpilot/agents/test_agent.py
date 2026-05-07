"""Test agent used to verify LLM configuration."""

from agents import Agent

from rfpilot.config.settings import settings

TEST_AGENT_INSTRTUCTIONS = """
You are a test agent, just to test LLM model configurations.

"""

test_agent = Agent(
    name="Test agent",
    instructions=TEST_AGENT_INSTRTUCTIONS,
    model=settings.DEEPSEEK_MODEL,
)
