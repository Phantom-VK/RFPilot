"""Cross-document consolidation agent for RFP and addendum results."""

# pylint: disable=import-error

from agents import Agent

from rfpilot.agents.base_agent import AGENT_DEFAULTS, MERGE_MODEL_SETTINGS


CONSOLIDATION_AGENT_INSTRUCTIONS = """
You receive a JSON array where each item is the full extraction from one document.
Documents are ordered: index 0 is the base RFP, subsequent indices are addendums or
supporting bid-information documents in order.
Start with the base RFP.
Addendum fields ALWAYS override earlier values when non-null.
Apply addendum overrides in order. The last addendum wins for direct conflicts such as due_date.
Supporting bid-information documents may enrich missing fields such as bid_number, title,
bid_submission_type, pre_bid_meeting, contact_info, and company_name.
For complementary fields, combine useful details instead of replacing them:
bid_summary, product, product_specification, additional_documentation, installation,
delivery_date, and contract_or_cooperative.
For contact_info, return an object when possible with department, name, phone, email,
address, and role.
Remove duplicate wording and markdown formatting.
Return one final merged JSON object with all 20 fields.
Return JSON only. Do not add commentary or markdown fences.
"""

consolidation_agent = Agent(
    name="ConsolidationAgent",
    instructions=CONSOLIDATION_AGENT_INSTRUCTIONS,
    model_settings=MERGE_MODEL_SETTINGS,
    **AGENT_DEFAULTS,
)
