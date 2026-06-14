from typing import Literal, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel


class DealFinancials(BaseModel):
    business_name: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    years_in_business: Optional[int] = None
    asking_price: Optional[float] = None
    down_payment: Optional[float] = None
    annual_revenue: Optional[float] = None
    sde: Optional[float] = None
    ebitda: Optional[float] = None
    gross_margin_pct: Optional[float] = None
    revenue_trend: Optional[str] = None
    multiple: Optional[float] = None
    real_estate_included: Optional[bool] = None
    inventory_value: Optional[float] = None
    owner_hours_per_week: Optional[int] = None
    reason_for_sale: Optional[str] = None
    extraction_notes: Optional[str] = None


@dataclass
class RuleResult:
    id: str
    label: str
    passed: bool
    weight: Literal["hard", "soft"]
    fail_reason: str = ""


@dataclass
class EvaluationResult:
    verdict: Literal["CALL", "PASS"]
    hard_fails: list[RuleResult] = field(default_factory=list)
    soft_fails: list[RuleResult] = field(default_factory=list)
    passes: list[RuleResult] = field(default_factory=list)

    @property
    def all_results(self) -> list[RuleResult]:
        return self.hard_fails + self.soft_fails + self.passes


class ScreeningReport(BaseModel):
    verdict: Literal["CALL", "PASS"]
    reasoning: str
    hard_fails: list[str]
    soft_flags: list[str]
    top_questions: list[str]
