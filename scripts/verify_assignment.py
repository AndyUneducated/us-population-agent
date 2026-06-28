#!/usr/bin/env python3
"""Verify ASSIGNMENT.md requirements: context, guardrails, graceful degradation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from census_agent.config import get_settings
from census_agent.eval.gate import run_quality_gate
from census_agent.eval.harness import load_cases, run_eval


def main() -> int:
    settings = get_settings()
    root = settings.project_root

    suites = {
        "golden": root / "evals" / "golden.jsonl",
        "degradation": root / "evals" / "phase4_degradation.jsonl",
        "context": root / "evals" / "assignment_context.jsonl",
    }

    print("Assignment verification")
    print("=" * 50)
    ok = True
    for name, path in suites.items():
        cases = load_cases(path)
        if name == "degradation":
            cases = [c for c in cases if not c.get("requires_llm")]
        report = run_eval(cases, settings)
        summary = report.summary()
        passed = summary["pass_rate"] == 1.0
        ok = ok and passed
        print(f"{name:12} {summary['passed']}/{summary['total']} pass_rate={summary['pass_rate']}")
        for r in report.results:
            if not r.passed:
                print(f"  FAIL {r.case_id}: {r.reason}")

    gate = run_quality_gate(settings=settings)
    print(f"quality_gate  {'PASS' if gate.passed else 'FAIL'} {gate.violations}")
    ok = ok and gate.passed
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
