"""Generate and analyze a fully synthetic OEM service reminder example."""

import csv
import hashlib
import json
import random
from collections import Counter
from math import erfc, sqrt
from pathlib import Path
from statistics import NormalDist


ROOT = Path(__file__).parent
PLAN = json.loads((ROOT / "plan.json").read_text(encoding="utf-8"))
CSV_PATH = ROOT / "synthetic_customers.csv"
RESULT_PATH = ROOT / "results.json"


def write_if_same_or_absent(path: Path, data: bytes) -> None:
    if path.exists() and path.read_bytes() != data:
        raise RuntimeError(f"Existing output differs: {path.name}")
    if not path.exists():
        path.write_bytes(data)


def wilson(events: int, total: int, z: float) -> tuple[float, float]:
    rate = events / total
    denominator = 1 + z * z / total
    center = (rate + z * z / (2 * total)) / denominator
    half = z * sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / denominator
    return center - half, center + half


def difference_interval(x_1: int, n_1: int, x_0: int, n_0: int, level: float) -> dict:
    p_1, p_0 = x_1 / n_1, x_0 / n_0
    z = NormalDist().inv_cdf((1 + level) / 2)
    low_1, high_1 = wilson(x_1, n_1, z)
    low_0, high_0 = wilson(x_0, n_0, z)
    delta = p_1 - p_0
    return {
        "difference_pp": 100 * delta,
        "ci_level": level,
        "ci_low_pp": 100 * (delta - sqrt((p_1 - low_1) ** 2 + (high_0 - p_0) ** 2)),
        "ci_high_pp": 100 * (delta + sqrt((high_1 - p_1) ** 2 + (p_0 - low_0) ** 2)),
    }


def pooled_p(x_1: int, n_1: int, x_0: int, n_0: int) -> float:
    p_1, p_0 = x_1 / n_1, x_0 / n_0
    pooled = (x_1 + x_0) / (n_1 + n_0)
    z = (p_1 - p_0) / sqrt(pooled * (1 - pooled) * (1 / n_1 + 1 / n_0))
    return erfc(abs(z) / sqrt(2))


rng = random.Random(PLAN["seed"])
eligibility = PLAN["eligibility"]
event_p = PLAN["assumed_event_probabilities"]
rows = []
funnel = Counter()
for customer_no in range(1, PLAN["population"] + 1):
    consent = rng.random() < eligibility["marketing_consent_probability"]
    due = rng.random() < eligibility["routine_service_due_30d_probability"]
    booked = rng.random() < eligibility["existing_booking_probability"]
    safety = rng.random() < eligibility["mandatory_safety_notice_probability"]
    funnel["consent"] += consent
    funnel["due"] += due
    funnel["existing_booking"] += booked
    funnel["mandatory_safety_notice"] += safety
    eligible = consent and due and not booked and not safety
    if eligible:
        arm = rng.choice(PLAN["assignment"]["arms"])
        assigned_day = rng.randrange(30)
        completed = rng.random() < event_p["completed_routine_service_visit_28d"][arm]
        optout = rng.random() < event_p["marketing_optout_28d"][arm]
        completion_day = rng.randint(1, 28) if completed else ""
        optout_day = rng.randint(1, 28) if optout else ""
        funnel["eligible"] += 1
    else:
        arm, assigned_day, completion_day, optout_day = "", "", "", ""
    rows.append((customer_no, int(consent), int(due), int(booked), int(safety),
                 int(eligible), arm, assigned_day, completion_day, optout_day))

header = ("customer_id", "marketing_consent", "routine_due_30d", "existing_booking",
          "mandatory_safety_notice", "eligible", "arm", "assigned_day",
          "completion_day_after_assignment", "optout_day_after_assignment")
from io import StringIO
buffer = StringIO(newline="")
writer = csv.writer(buffer, lineterminator="\n")
writer.writerow(header)
writer.writerows(rows)
csv_data = buffer.getvalue().encode("utf-8")
write_if_same_or_absent(CSV_PATH, csv_data)

by_arm = {arm: Counter() for arm in PLAN["assignment"]["arms"]}
interim = Counter()
for row in rows:
    arm = row[6]
    if not arm:
        continue
    by_arm[arm]["assigned"] += 1
    by_arm[arm]["completed_28"] += bool(row[8])
    by_arm[arm]["optout_28"] += bool(row[9])
    interim["assigned_by_day_28"] += row[7] <= 28
    interim["mature_by_day_28"] += row[7] + 28 <= 28

family = PLAN["primary"]["comparisons"]
comparisons = {}
for label in family:
    treatment, reference = label.split("-")
    x_1, n_1 = by_arm[treatment]["completed_28"], by_arm[treatment]["assigned"]
    x_0, n_0 = by_arm[reference]["completed_28"], by_arm[reference]["assigned"]
    comparison = difference_interval(x_1, n_1, x_0, n_0,
                                     1 - PLAN["primary"]["family_alpha"] / len(family))
    comparison["bonferroni_p"] = min(1.0, len(family) * pooled_p(x_1, n_1, x_0, n_0))
    comparisons[label] = comparison
interval = comparisons["B-A"]
guardrail = difference_interval(by_arm["B"]["optout_28"], by_arm["B"]["assigned"],
                                by_arm["A"]["optout_28"], by_arm["A"]["assigned"], 0.95)
business_min = PLAN["decision"]["illustrative_minimum_business_improvement_pp"]
optout_limit = PLAN["decision"]["illustrative_optout_worsening_limit_pp"]
results = {
    "status": "synthetic_education_only",
    "plan_sha256": hashlib.sha256((ROOT / "plan.json").read_bytes()).hexdigest(),
    "synthetic_csv_sha256": hashlib.sha256(csv_data).hexdigest(),
    "population": PLAN["population"],
    "funnel": dict(funnel),
    "by_arm": {arm: dict(counts) for arm, counts in by_arm.items()},
    "interim_day_28": dict(interim),
    "primary_comparisons": comparisons,
    "primary_B_minus_A": interval,
    "exploratory_optout_B_minus_A": guardrail,
    "decision": {
        "completed_winner_evidence_in_synthetic_model": interval["ci_low_pp"] > 0,
        "minimum_business_improvement_supported": interval["ci_low_pp"] >= business_min,
        "optout_limit_ruled_out": guardrail["ci_high_pp"] <= optout_limit,
        "capacity_verified": False,
        "rollout": "hold; B remains a candidate for further review"
    }
}
json_data = (json.dumps(results, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
write_if_same_or_absent(RESULT_PATH, json_data)
print(json.dumps(results, ensure_ascii=False, indent=2))
