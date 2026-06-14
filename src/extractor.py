import json
import os
from typing import Optional
from dotenv import load_dotenv
import anthropic
from pydantic import BaseModel, Field

load_dotenv()


class DealFinancials(BaseModel):
    # Listing basics
    business_name: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    years_in_business: Optional[int] = None

    # Pricing
    asking_price: Optional[float] = None
    down_payment: Optional[float] = None

    # Income
    annual_revenue: Optional[float] = None
    sde: Optional[float] = None          # Seller's Discretionary Earnings
    ebitda: Optional[float] = None

    # Derived / stated metrics
    gross_margin_pct: Optional[float] = None
    revenue_trend: Optional[str] = None  # "growing", "stable", "declining", "unknown"
    multiple: Optional[float] = None     # asking price / SDE or EBITDA

    # Deal structure hints
    real_estate_included: Optional[bool] = None
    inventory_value: Optional[float] = None
    owner_hours_per_week: Optional[int] = None
    reason_for_sale: Optional[str] = None

    # Raw notes that don't fit above fields
    extraction_notes: Optional[str] = None


SYSTEM_PROMPT = """You are a business acquisition analyst. Your job is to extract structured financial
and operational data from business-for-sale listings (typically BizBuySell style).

Extract every number you can find. When a value is not stated, return null — never guess or fabricate.
For revenue_trend, infer from any year-over-year data mentioned: "growing", "stable", "declining", or "unknown".
For multiple, calculate asking_price / sde if both are present, otherwise asking_price / ebitda.
All dollar values should be plain numbers (no $ or commas) in USD.
Put any ambiguous or notable details in extraction_notes."""

EXTRACTION_PROMPT = """Extract the key financials and deal details from this business listing and return them as JSON.

LISTING:
{listing_text}

Return a JSON object matching exactly this schema (use null for missing fields):
{schema}"""


def extract(listing_text: str) -> DealFinancials:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    schema = json.dumps(DealFinancials.model_json_schema(), indent=2)
    prompt = EXTRACTION_PROMPT.format(listing_text=listing_text, schema=schema)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    data = json.loads(raw.strip())
    return DealFinancials(**data)


if __name__ == "__main__":
    sample = """
    Profitable HVAC Company – Established 18 Years
    Asking Price: $1,200,000
    Cash Flow: $320,000
    Gross Revenue: $2,100,000
    EBITDA: $310,000
    FF&E: $150,000
    Inventory: $40,000
    Established: 2006

    Well-established HVAC service and installation company serving a 3-county area in central Ohio.
    Revenue has grown from $1.8M to $2.1M over the past three years. Owner works approximately
    40 hours/week and is looking to retire. Real estate not included – lease in place at $3,200/month.
    Down payment of $300,000 required for SBA financing.
    """

    result = extract(sample)
    print(result.model_dump_json(indent=2))
