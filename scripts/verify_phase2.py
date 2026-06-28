#!/usr/bin/env python3
"""Phase 2 acceptance: end-to-end agent + eval harness."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from census_agent.agent.orchestrator import CensusAgent
from census_agent.eval.harness import run_eval


def main() -> int:
    errors: list[str] = []

    sample_questions = [
        "What is the total population of California?",
        "What is the median household income in Texas?",
        "What is the median age in the United States?",
    ]
    with CensusAgent() as agent:
        for q in sample_questions:
            resp = agent.ask(q)
            if resp.refused or resp.error or not resp.sql:
                errors.append(f"E2E fail {q!r}: {resp.error or resp.answer[:80]}")
            else:
                print(f"OK E2E: {q!r} -> value={resp.rows[0].get('value') if resp.rows else '?'}")

    report = run_eval()
    summary = report.summary()
    print(f"\nEval: {summary['passed']}/{summary['total']} passed ({summary['pass_rate']})")
    for r in report.results:
        status = "OK" if r.passed else "FAIL"
        print(f"  {status} {r.case_id}: {r.reason} ({r.latency_ms:.0f}ms)")
        if not r.passed:
            errors.append(f"eval {r.case_id}: {r.reason}")

    # Require at least 7/10 on golden set (allow follow-up + religion edge cases)
    if summary["passed"] < 7:
        errors.append(f"eval pass rate too low: {summary['pass_rate']}")

    if errors:
        print("\nPhase 2 FAILED:")
        for e in errors:
            print(" -", e)
        return 1
    print("\nPhase 2 acceptance: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
