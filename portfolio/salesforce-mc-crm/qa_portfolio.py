"""Check the public portfolio text against its local synthetic evidence."""

import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).parent
MAIN = ROOT / "허재혁_MC_CRM_포트폴리오_본문_20261118_v14.md"
DEMO = ROOT / "service_revisit_demo"
text = MAIN.read_text(encoding="utf-8")
results = json.loads((DEMO / "results.json").read_text(encoding="utf-8"))
plan = json.loads((DEMO / "plan.json").read_text(encoding="utf-8"))

headings = re.findall(r"^## (\d+)쪽\.", text, flags=re.MULTILINE)
assert headings == [str(n) for n in range(1, 12)], headings
assert "·" not in text
assert "→" not in text
assert "ab_test_demo" not in text
assert "0.93%p" not in text
assert "AI 협업 합성 실습 초안" in text
assert "저는 예약 클릭보다" in text
assert "실제 적용 기준은 현장의 사업 가치" in text
assert "30일 대상 조건과 28일 관측은 교육용 가정" in text
assert "제한적 적용 여부를 재검토" in text
assert "실제 MC 계정" in text

documents = [
    MAIN,
    ROOT / "README.md",
    ROOT / "QA.md",
    ROOT / "MC_JOURNEY_QA.md",
    ROOT / "본인_검토_20261118_v3.md",
    ROOT / "면접_설명_준비_20261118_v3.md",
    ROOT / "service_revisit_demo/README.md",
    ROOT / "not_sent_demo/README.md",
    ROOT.parent.parent / "README.md",
]
local_links = []
for document in documents:
    content = document.read_text(encoding="utf-8")
    if document != ROOT.parent.parent / "README.md":
        assert "·" not in content, document
    for link in re.findall(r"\]\(((?:\./|\.\./)[^)#]+)(?:#[^)]+)?\)", content):
        local_links.append((document, link))
missing = []
for document, link in local_links:
    path = link.split("#", 1)[0]
    if not (document.parent / path).exists():
        missing.append((str(document), link))
assert not missing, missing

seen = set()
counts = {arm: Counter() for arm in "ABH"}
interim = Counter()
eligible_count = 0
with (DEMO / "synthetic_customers.csv").open(encoding="utf-8", newline="") as stream:
    for row in csv.DictReader(stream):
        customer = row["customer_id"]
        assert customer not in seen, customer
        seen.add(customer)
        eligible = (
            row["marketing_consent"] == "1"
            and row["routine_due_30d"] == "1"
            and row["existing_booking"] == "0"
            and row["mandatory_safety_notice"] == "0"
        )
        assert (row["eligible"] == "1") == eligible
        if not eligible:
            assert not row["arm"] and not row["assigned_day"]
            continue
        eligible_count += 1
        arm = row["arm"]
        assert arm in counts
        day = int(row["assigned_day"])
        assert 0 <= day <= 29
        counts[arm]["assigned"] += 1
        for field, metric in (
            ("completion_day_after_assignment", "completed_28"),
            ("optout_day_after_assignment", "optout_28"),
        ):
            if row[field]:
                assert 1 <= int(row[field]) <= 28
                counts[arm][metric] += 1
        interim["assigned_by_day_28"] += day <= 28
        interim["mature_by_day_28"] += day + 28 <= 28

assert len(seen) == plan["population"] == results["population"]
assert eligible_count == results["funnel"]["eligible"]
assert {key: dict(value) for key, value in counts.items()} == results["by_arm"]
assert dict(interim) == results["interim_day_28"]
assert abs(results["primary_comparisons"]["B-A"]["difference_pp"] - 1.089106022964871) < 1e-9
assert all(results["primary_comparisons"][pair]["ci_low_pp"] > 0 for pair in ("B-A", "A-H", "B-H"))
assert not results["decision"]["minimum_business_improvement_supported"]
assert not results["decision"]["optout_limit_ruled_out"]
assert "46,621명" in text and "+1.09%p" in text and "1,483명" in text

for file in ROOT.rglob("*"):
    if not file.is_file() or ".git" in file.parts or file.suffix == ".pyc":
        continue
    if file.suffix not in {".md", ".py", ".json", ".csv"}:
        continue
    content = file.read_text(encoding="utf-8")
    assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", content), file
    assert not re.search(r"C:[/\\]Users[/\\]", content), file
    assert not re.search(r"\b(?:sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16})\b", content), file

print(json.dumps({
    "pages_in_order": len(headings),
    "local_links_checked": len(local_links),
    "synthetic_population": len(seen),
    "eligible": eligible_count,
    "primary_B_minus_A_pp": results["primary_comparisons"]["B-A"]["difference_pp"],
    "status": "local checks passed; human review and MC account QA remain"
}, ensure_ascii=False, indent=2))
