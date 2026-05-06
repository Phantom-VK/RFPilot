"""Document-level reducer agent for partial RFP extractions."""

# pylint: disable=import-error
from agents import Agent

from rfpilot.agents.base_agent import AGENT_DEFAULTS, MERGE_MODEL_SETTINGS


MERGER_AGENT_INSTRUCTIONS = """
You receive a JSON array of partial extraction objects from different chunks of the same document.
Many fields will be null across most objects.
Your job: merge them into one final JSON object.
Rules:
(1) prefer the most specific non-null value,
(2) if two chunks have different non-null values for the same field, prefer the one with more detail,
(3) for list fields like product_specification, concatenate unique values. Return a single valid JSON object with all 20 fields.
Return JSON only. Do not add commentary or markdown fences.
"""

merger_agent = Agent(
    name="MergerAgent",
    instructions=MERGER_AGENT_INSTRUCTIONS,
    model_settings=MERGE_MODEL_SETTINGS,
    **AGENT_DEFAULTS,
)
