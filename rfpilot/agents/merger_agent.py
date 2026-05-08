"""Document-level reducer agent for partial RFP extractions."""

# pylint: disable=import-error

from agents import Agent

from rfpilot.agents.base_agent import AGENT_DEFAULTS, MERGE_MODEL_SETTINGS


MERGER_AGENT_INSTRUCTIONS = """
You receive a JSON array of partial extraction objects from different chunks of the same document.
Many fields will be null across most objects.
Your job: merge them into one final JSON object.
Rules:
(1) return all 20 fields exactly once,
(2) ignore null, empty string, empty array, and empty object values,
(3) prefer the most specific non-null value,
(4) if two chunks have different non-null values for the same field, keep the value with more useful procurement detail,
(5) combine complementary details for bid_summary, product, product_specification,
    additional_documentation, installation, delivery_date, and contract_or_cooperative,
(6) for contact_info, return an object when possible and merge department, name, phone,
    email, address, and role from all chunks,
(7) remove duplicate wording and markdown formatting,
(8) keep concise output, but do not drop important requirements.
Return JSON only. Do not add commentary or markdown fences.
"""

merger_agent = Agent(
    name="MergerAgent",
    instructions=MERGER_AGENT_INSTRUCTIONS,
    model_settings=MERGE_MODEL_SETTINGS,
    **AGENT_DEFAULTS,
)
