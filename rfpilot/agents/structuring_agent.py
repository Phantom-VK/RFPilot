"""Chunk-level RFP extraction agent."""

# pylint: disable=import-error

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

FIELD_GUIDANCE = """
Field guidance:
- bid_number: solicitation, sourcing, bid, RFP, event, or reference number.
- title: plain bid/RFP title without markdown formatting.
- due_date: final submission due date. If an addendum extends the due date, extract the new date.
- bid_submission_type: solicitation type such as RFP, IFB, RFQ, informal/formal.
- term_of_bid: contract term, renewals, extensions, maximum term.
- pre_bid_meeting: pre-bid/pre-proposal meeting date, time, location, or virtual details.
- installation: deployment, installation, white glove, asset tagging/decaling, etching,
  imaging, delivery-to-site, setup, or rollout requirements.
- bid_bond_requirement: bid bond, proposal bond, surety, bond percentage, or explicit no-bond text.
- delivery_date: required delivery date, expected delivery window, first order date, rollout timing.
- payment_terms: net terms, invoice timing, payment schedule, retainage, or payment method.
- additional_documentation: required forms, attachments, certificates, W-9, Form 1295,
  MWBE forms, affidavits, insurance, punch-out documents, or other submission documents.
- mfg_for_registration: manufacturer registration, manufacturer authorization, reseller
  authorization, manufacturer number, or vendor registration requirements.
- contract_or_cooperative: cooperative purchasing, rider, interlocal agreement, EPCNT,
  CTPA, purchasing alliance, or piggyback language.
- model_no: explicit model numbers only.
- part_no: explicit part/SKU numbers only.
- product: product or service category being purchased.
- contact_info: return an object when possible with keys such as department, name, phone,
  email, address, and role.
- company_name: issuing agency, district, buyer, or organization name.
- bid_summary: concise 2-4 sentence summary of the solicitation content in this chunk batch.
- product_specification: concrete technical/specification requirements. Include useful
  tier/category names and numeric requirements.
"""

STRUCTURING_AGENT_INSTRUCTIONS = f"""
You are an RFP data extraction specialist.
You will receive one small batch containing one or more chunks of an RFP document.
Each chunk is labeled with its section, type, and index.
Extract ONLY the fields you can find in the provided chunk batch.
For fields not present in the chunk batch, return null.
Use the field guidance below to map procurement language to the correct schema field.
Do not require exact field-name matches if the chunk clearly contains the same concept.
Never hallucinate values.
Dates must be returned as written.
Return a valid JSON object with exactly these keys: {RFP_FIELD_NAMES}.
Return JSON only. Do not add commentary or markdown fences.

{FIELD_GUIDANCE}

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
