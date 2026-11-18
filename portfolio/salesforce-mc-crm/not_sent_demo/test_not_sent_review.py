"""Check the decisions that matter before sharing the synthetic example."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from not_sent_review import review_rows, write_results


HERE = Path(__file__).parent


class NotSentReviewTests(unittest.TestCase):
    def test_protected_contacts_are_never_retried(self) -> None:
        rows = review_rows(HERE / "sample_not_sent.csv", "JOB-CASE-001")
        self.assertEqual(len(rows), 7)
        self.assertEqual(sum(row["분류"] == "보호 유지" for row in rows), 4)
        self.assertTrue(all(row["자동 재발송"] == "아니오" for row in rows))
        self.assertEqual(rows[-1]["분류"], "사람 확인")
        with tempfile.TemporaryDirectory() as temp:
            summary = write_results(rows, Path(temp))
            self.assertEqual(summary["검토 행"], 7)
            self.assertEqual(summary["자동 재발송 건수"], 0)

    def test_wrong_job_is_excluded_and_missing_job_fails(self) -> None:
        rows = review_rows(HERE / "sample_not_sent.csv", "JOB-OTHER-002")
        self.assertEqual([row["SubscriberKey"] for row in rows], ["T08"])
        with self.assertRaises(ValueError):
            review_rows(HERE / "sample_not_sent.csv", "NOT-THERE")

    def test_duplicate_subscriber_is_not_silently_counted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "duplicate.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["JobID", "SubscriberKey", "Reason"])
                writer.writerow(["JOB-1", "T01", "Held"])
                writer.writerow(["JOB-1", "T01", "Held"])
            with self.assertRaises(ValueError):
                review_rows(path, "JOB-1")

    def test_missing_required_column_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "missing.csv"
            path.write_text("JobID,SubscriberKey\nJOB-1,T01\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                review_rows(path, "JOB-1")


if __name__ == "__main__":
    unittest.main()
