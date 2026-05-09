"""Chunk-level RFP extraction agent."""

# pylint: disable=import-error

from agents import Agent

from rfpilot.agents.base_agent import AGENT_DEFAULTS, EXTRACTION_MODEL_SETTINGS
from rfpilot.agents.prompts import STRUCTURING_AGENT_INSTRUCTIONS

structuring_agent = Agent(
    name="StructuringAgent",
    instructions=STRUCTURING_AGENT_INSTRUCTIONS,
    model_settings=EXTRACTION_MODEL_SETTINGS,
    **AGENT_DEFAULTS,
)
