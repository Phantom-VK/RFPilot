from agents import Agent

from rfpilot.agents.base_agent import AGENT_DEFAULTS, EXTRACTION_MODEL_SETTINGS


RFP_FIELD_NAMES = [
    "bid_number",
    "title",
    "due_date",
    "bid_submission_type",
    "term_of_bid",
    "pre_bid_meeting",
    "installation",
    "bid_bond_requirement",
    "delivery_date",
    "payment_terms",
    "additional_documentation",
    "mfg_for_registration",
    "contract_or_cooperative",
    "model_no",
    "part_no",
    "product",
    "contact_info",
    "company_name",
    "bid_summary",
    "product_specification",
]

STRUCTURING_AGENT_INSTRUCTIONS = f"""
You are an RFP data extraction specialist. 
You will receive ONE chunk of an RFP document labeled with its section, type, and index. 
Extract ONLY the fields you can find in this chunk. 
For fields not present in this chunk, return null. 
Never hallucinate values. Return a valid JSON object with exactly these keys: {RFP_FIELD_NAMES}. 
Dates must be returned as written. Do not add commentary.

Example JSON output shape:
{{
  "bid_number": null,
  "title": null,
  "due_date": null,
  "bid_submission_type": null,
  "term_of_bid": null,
  "pre_bid_meeting": null,
  "installation": null,
  "bid_bond_requirement": null,
  "delivery_date": null,
  "payment_terms": null,
  "additional_documentation": null,
  "mfg_for_registration": null,
  "contract_or_cooperative": null,
  "model_no": null,
  "part_no": null,
  "product": null,
  "contact_info": null,
  "company_name": null,
  "bid_summary": null,
  "product_specification": null
}}
"""

structuring_agent = Agent(
    name="StructuringAgent",
    instructions=STRUCTURING_AGENT_INSTRUCTIONS,
    model_settings=EXTRACTION_MODEL_SETTINGS,
    **AGENT_DEFAULTS,
)
