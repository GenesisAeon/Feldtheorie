#!/usr/bin/env python3
"""Compute a UTAC status drift score from readiness and documentation targets.

The score tracks ζ(R)-relevant divergence between the declared narrative layer and
runtime filesystem truth.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Readiness report not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def _parse_iso_utc(iso_value: str) -> dt.datetime:
    normalized = iso_value.replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _count_missing_doc_targets(report: dict[str, Any]) -> int:
    missing = 0
    for target in report.get("doc_targets", []):
        if not bool(target.get("exists")):
            missing += 1
        for output in target.get("expected_outputs", []):
            if not bool(output.get("exists")):
                missing += 1
    return missing


def _extract_test_report_age_days(test_report: Path) -> int | None:
    if not test_report.exists():
        return None

    content = test_report.read_text(encoding="utf-8")
    match = re.search(r"^\*\*Datum:\*\*\s*(\d{4}-\d{2}-\d{2})\s*$", content, flags=re.MULTILINE)
    if not match:
        return None

    report_date = dt.datetime.strptime(match.group(1), "%Y-%m-%d").date()
    today = dt.datetime.now(dt.timezone.utc).date()
    return max(0, (today - report_date).days)


def compute_status_drift(
    report: dict[str, Any],
    *,
    max_age_days: int | None,
    test_report_age_days: int | None,
    max_test_report_age_days: int | None,
) -> dict[str, Any]:
    drift_info = report.get("declared_actual_drift", {})
    mismatch_count = int(drift_info.get("mismatch_count", 0))
    missing_docs = _count_missing_doc_targets(report)

    freshness_age_days: int | None = None
    stale_penalty = 0
    generated_at = report.get("meta", {}).get("generated_at")
    if generated_at:
        generated_at_dt = _parse_iso_utc(str(generated_at))
        now = dt.datetime.now(dt.timezone.utc)
        freshness_age_days = max(0, (now - generated_at_dt).days)
        if max_age_days is not None and freshness_age_days > max_age_days:
            stale_penalty = freshness_age_days - max_age_days

    test_report_stale_penalty = 0
    if (
        max_test_report_age_days is not None
        and test_report_age_days is not None
        and test_report_age_days > max_test_report_age_days
    ):
        test_report_stale_penalty = test_report_age_days - max_test_report_age_days

    status_drift_score = mismatch_count + missing_docs + stale_penalty + test_report_stale_penalty
    return {
        "status_drift_score": status_drift_score,
        "declared_actual_mismatches": mismatch_count,
        "missing_doc_targets": missing_docs,
        "readiness_age_days": freshness_age_days,
        "stale_penalty": stale_penalty,
        "test_report_age_days": test_report_age_days,
        "test_report_stale_penalty": test_report_stale_penalty,
        "max_age_days": max_age_days,
        "max_test_report_age_days": max_test_report_age_days,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute a status drift score for analysis/reports/utac_v2_readiness.json",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("analysis/reports/utac_v2_readiness.json"),
        help="Readiness report in JSON format.",
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=14,
        help="Maximum freshness age before stale penalty is added (set <0 to disable).",
    )
    parser.add_argument(
        "--test-report",
        type=Path,
        default=Path("TEST_REPORT.md"),
        help="Path to the test status report with a '**Datum:** YYYY-MM-DD' header.",
    )
    parser.add_argument(
        "--max-test-report-age-days",
        type=int,
        default=30,
        help="Maximum age for TEST_REPORT.md before drift penalty is added (set <0 to disable).",
    )
    args = parser.parse_args()

    max_age_days = None if args.max_age_days < 0 else args.max_age_days
    max_test_report_age_days = (
        None if args.max_test_report_age_days < 0 else args.max_test_report_age_days
    )

    try:
        report = _load_json(args.json)
        summary = compute_status_drift(
            report,
            max_age_days=max_age_days,
            test_report_age_days=_extract_test_report_age_days(args.test_report),
            max_test_report_age_days=max_test_report_age_days,
        )
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"❌ status drift check failed: {exc}")
        return 2

    print(
        "status_drift_score={score} (mismatches={mismatch}, missing_docs={docs}, "
        "readiness_age_days={age}, stale_penalty={stale}, "
        "test_report_age_days={test_report_age}, test_report_stale_penalty={test_report_stale})".format(
            score=summary["status_drift_score"],
            mismatch=summary["declared_actual_mismatches"],
            docs=summary["missing_doc_targets"],
            age=summary["readiness_age_days"],
            stale=summary["stale_penalty"],
            test_report_age=summary["test_report_age_days"],
            test_report_stale=summary["test_report_stale_penalty"],
        )
    )

    if summary["status_drift_score"] != 0:
        print("❌ status drift gate failed: expected score == 0")
        return 1

    print("✅ status drift gate clear (σ(β(R-Θ)) telemetry synchronized)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
