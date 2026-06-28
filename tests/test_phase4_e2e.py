"""Phase 4 E2E tests with optional Gemini model calls."""

from __future__ import annotations

from pathlib import Path

import pytest

from census_agent.config import get_settings
from census_agent.eval.harness import load_cases, run_eval


@pytest.mark.e2e
def test_phase4_degradation_deterministic() -> None:
    root = get_settings().project_root
    cases = [
        c
        for c in load_cases(root / "evals" / "phase4_degradation.jsonl")
        if not c.get("requires_llm")
    ]
    report = run_eval(cases)
    summary = report.summary()
    assert summary["passed"] >= summary["total"] - 1, [
        (r.case_id, r.reason) for r in report.results if not r.passed
    ]


@pytest.mark.e2e
def test_phase4_llm_sql_path(require_gemini: None) -> None:
    settings = get_settings()
    if not settings.embedding_index_path.exists():
        pytest.skip("field index missing")

    cases = [
        c
        for c in load_cases(settings.project_root / "evals" / "phase4_degradation.jsonl")
        if c.get("requires_llm")
    ]
    report = run_eval(cases, settings)
    assert all(r.passed for r in report.results), [
        (r.case_id, r.reason) for r in report.results if not r.passed
    ]
