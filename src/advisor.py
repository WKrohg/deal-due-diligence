import json
import os
from dotenv import load_dotenv
import anthropic
from models import DealFinancials, EvaluationResult, ScreeningReport

load_dotenv()

SYSTEM_PROMPT = """You are a seasoned small business acquisition analyst helping a buyer decide whether to
pursue a deal. You will receive structured financials and rule evaluation results for a business listing.

Your job:
1. Write a concise 2-4 sentence reasoning narrative explaining the verdict.
2. Summarize any hard disqualifiers and soft flags in plain English (not raw rule IDs).
3. Generate exactly 3 sharp, specific questions the buyer should ask the seller before getting on a call.
   Draw questions from: soft flags, owner hours, reason for sale, revenue trend, and extraction notes.
   Questions should probe risks, not confirm basics already stated in the listing.

Return only valid JSON matching the schema provided. Never fabricate financials."""

ADVISE_PROMPT = """Evaluate this deal and return a JSON ScreeningReport.

FINANCIALS:
{financials}

EVALUATION:
Verdict: {verdict}
Hard fails: {hard_fails}
Soft flags: {soft_flags}

Return JSON matching this schema exactly:
{schema}"""


def advise(financials: DealFinancials, evaluation: EvaluationResult) -> ScreeningReport:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    hard_fails = [r.fail_reason for r in evaluation.hard_fails]
    soft_flags = [r.fail_reason for r in evaluation.soft_fails]
    schema = json.dumps(ScreeningReport.model_json_schema(), indent=2)

    prompt = ADVISE_PROMPT.format(
        financials=financials.model_dump_json(indent=2),
        verdict=evaluation.verdict,
        hard_fails=hard_fails or "None",
        soft_flags=soft_flags or "None",
        schema=schema,
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return ScreeningReport(**json.loads(raw.strip()))
