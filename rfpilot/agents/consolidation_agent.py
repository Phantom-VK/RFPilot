"""Cross-document consolidation agent for RFP and addendum results."""

# pylint: disable=import-error
from agents import Agent

from rfpilot.agents.base_agent import AGENT_DEFAULTS, MERGE_MODEL_SETTINGS


CONSOLIDATION_AGENT_INSTRUCTIONS = """
You receive a JSON array where each item is the full extraction from one document.
Documents are ordered: index 0 is the base RFP, subsequent indices are addendums in order.
Addendum fields ALWAYS override base RFP fields when non-null.
Apply overrides in order (last addendum wins).
Return one final merged JSON object with all 20 fields.
Return JSON only. Do not add commentary or markdown fences.
"""

consolidation_agent = Agent(
    name="ConsolidationAgent",
    instructions=CONSOLIDATION_AGENT_INSTRUCTIONS,
    model_settings=MERGE_MODEL_SETTINGS,
    **AGENT_DEFAULTS,
)
