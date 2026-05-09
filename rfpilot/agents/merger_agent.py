"""Document-level reducer agent for partial RFP extractions."""

# pylint: disable=import-error

from agents import Agent

from rfpilot.agents.base_agent import AGENT_DEFAULTS, MERGE_MODEL_SETTINGS
from rfpilot.agents.prompts import MERGER_AGENT_INSTRUCTIONS

merger_agent = Agent(
    name="MergerAgent",
    instructions=MERGER_AGENT_INSTRUCTIONS,
    model_settings=MERGE_MODEL_SETTINGS,
    **AGENT_DEFAULTS,
)
