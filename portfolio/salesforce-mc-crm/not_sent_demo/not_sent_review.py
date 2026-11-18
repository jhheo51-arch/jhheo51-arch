"""Review a synthetic Not Sent extract. This does not connect to Marketing Cloud."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


REQUIRED_COLUMNS = {"JobID", "SubscriberKey", "Reason"}
RULES = {
    "Held": ("보호 유지", "주소와 구독자 상태를 확인하기 전에는 재발송하지 않음"),
    "Unsubscribed Master": ("보호 유지", "상업성 발송 대상에서 계속 제외"),
    "Account Level Opt Out": ("보호 유지", "계정 단위 수신거부 상태를 유지"),
    "Domain Exclusion": ("보호 유지", "제외 정책과 적용 범위를 확인하고 발송하지 않음"),
    "List Detective Exclusion": ("원천 확인", "원천 주소를 확인하고 수정한 뒤 시험"),
    "Build Email Error or Send Failure": (
        "콘텐츠 확인",
        "콘텐츠와 개인화 변수를 수정하고 시험한 뒤 적격 고객만 재검토",
    ),
}


def review_rows(input_path: Path, job_id: str) -> list[dict[str, str]]:
    with input_path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            missing = REQUIRED_COLUMNS - set(reader.fieldnames or ())
            raise ValueError(f"필수 열 누락: {', '.join(sorted(missing))}")

        reviewed: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for row in reader:
            if (row.get("JobID") or "").strip() != job_id:
                continue
            subscriber = (row.get("SubscriberKey") or "").strip()
            if not subscriber:
                raise ValueError("SubscriberKey가 빈 행이 있습니다")
            identity = (job_id, subscriber)
            if identity in seen:
                raise ValueError(f"같은 발송의 중복 SubscriberKey: {subscriber}")
            seen.add(identity)

            reason = (row.get("Reason") or "").strip()
            category, action = RULES.get(
                reason, ("사람 확인", "Reason과 발송 설정을 사람이 확인할 때까지 재발송 보류")
            )
            reviewed.append(
                {
                    "JobID": job_id,
                    "SubscriberKey": subscriber,
                    "Reason": reason,
                    "분류": category,
                    "다음 확인": action,
                    "자동 재발송": "아니오",
                }
            )
    if not reviewed:
        raise ValueError(f"선택한 JobID에 해당하는 행이 없습니다: {job_id}")
    return reviewed


def write_results(rows: list[dict[str, str]], out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    fields = ["JobID", "SubscriberKey", "Reason", "분류", "다음 확인", "자동 재발송"]
    with (out_dir / "reviewed_rows.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "자료 유형": "가상 Not Sent 검토용 예시",
        "선택 JobID": rows[0]["JobID"],
        "검토 행": len(rows),
        "분류별 건수": dict(sorted(Counter(row["분류"] for row in rows).items())),
        "자동 재발송 건수": sum(row["자동 재발송"] == "예" for row in rows),
        "제한": "실제 Marketing Cloud 추출, 발송 또는 QA 결과가 아님",
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_results(review_rows(args.input, args.job_id), args.out_dir), ensure_ascii=False))


if __name__ == "__main__":
    main()
