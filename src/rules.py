import os
import yaml
from models import DealFinancials, RuleResult, EvaluationResult

RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "rules", "diligence_rules.yaml")

OPERATORS = {
    "gte": lambda a, b: a >= b,
    "lte": lambda a, b: a <= b,
    "gt":  lambda a, b: a > b,
    "lt":  lambda a, b: a < b,
    "eq":  lambda a, b: a == b,
    "neq": lambda a, b: a != b,
    "in":      lambda a, b: a in b,
    "not_in":  lambda a, b: a not in b,
}


def _load_rules() -> list[dict]:
    with open(RULES_PATH) as f:
        return yaml.safe_load(f)["rules"]


def evaluate(financials: DealFinancials) -> EvaluationResult:
    rules = _load_rules()
    data = financials.model_dump()

    hard_fails, soft_fails, passes = [], [], []

    for rule in rules:
        field_val = data.get(rule["field"])

        # Skip rule if field wasn't extracted
        if field_val is None:
            continue

        op = OPERATORS.get(rule["operator"])
        if op is None:
            raise ValueError(f"Unknown operator: {rule['operator']}")

        passed = op(field_val, rule["value"])
        result = RuleResult(
            id=rule["id"],
            label=rule["label"],
            passed=passed,
            weight=rule["weight"],
            fail_reason="" if passed else rule["fail_reason"],
        )

        if passed:
            passes.append(result)
        elif rule["weight"] == "hard":
            hard_fails.append(result)
        else:
            soft_fails.append(result)

    verdict = "PASS" if hard_fails else "CALL"
    return EvaluationResult(verdict=verdict, hard_fails=hard_fails, soft_fails=soft_fails, passes=passes)


if __name__ == "__main__":
    # Test with a mock extraction result
    sample = DealFinancials(
        business_name="Acme HVAC",
        industry="HVAC",
        asking_price=1_200_000,
        sde=320_000,
        annual_revenue=2_100_000,
        multiple=3.75,
        years_in_business=18,
        revenue_trend="growing",
        owner_hours_per_week=40,
    )

    result = evaluate(sample)
    print(f"VERDICT: {result.verdict}\n")

    if result.hard_fails:
        print("HARD FAILS:")
        for r in result.hard_fails:
            print(f"  ✗ [{r.label}] {r.fail_reason}")

    if result.soft_fails:
        print("SOFT FLAGS:")
        for r in result.soft_fails:
            print(f"  ~ [{r.label}] {r.fail_reason}")

    if result.passes:
        print("PASSED:")
        for r in result.passes:
            print(f"  ✓ [{r.label}]")
