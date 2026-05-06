from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class RFPExtraction(BaseModel):
    """Structured extraction output for an RFP document set."""

    model_config = ConfigDict(extra="ignore")

    bid_number: Optional[str] = None
    title: Optional[str] = None
    due_date: Optional[str] = None
    bid_submission_type: Optional[str] = None
    term_of_bid: Optional[str] = None
    pre_bid_meeting: Optional[str] = None
    installation: Optional[str] = None
    bid_bond_requirement: Optional[str] = None
    delivery_date: Optional[str] = None
    payment_terms: Optional[str] = None
    additional_documentation: Optional[str] = None
    mfg_for_registration: Optional[str] = None
    contract_or_cooperative: Optional[str] = None
    model_no: Optional[str] = None
    part_no: Optional[str] = None
    product: Optional[str] = None
    contact_info: Optional[dict[str, Any]] = None
    company_name: Optional[str] = None
    bid_summary: Optional[str] = None
    product_specification: Optional[str] = None

    @classmethod
    def merge(cls, base: "RFPExtraction", override: "RFPExtraction") -> "RFPExtraction":
        """Return a new extraction with non-null override fields applied to base."""
        merged = base.model_dump()
        override_data = override.model_dump(exclude_none=True)
        merged.update(override_data)
        return cls.model_validate(merged)
