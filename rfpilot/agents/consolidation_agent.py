"""Cross-document consolidation agent for RFP and addendum results."""

# pylint: disable=import-error

from agents import Agent

from rfpilot.agents.base_agent import AGENT_DEFAULTS, MERGE_MODEL_SETTINGS
from rfpilot.agents.prompts import CONSOLIDATION_AGENT_INSTRUCTIONS

consolidation_agent = Agent(
    name="ConsolidationAgent",
    instructions=CONSOLIDATION_AGENT_INSTRUCTIONS,
    model_settings=MERGE_MODEL_SETTINGS,
    **AGENT_DEFAULTS,
)
