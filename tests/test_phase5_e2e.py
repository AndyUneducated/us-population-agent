"""Phase 5 quality gate and model regression E2E."""

from __future__ import annotations

import pytest

from census_agent.config import get_settings
from census_agent.eval.gate import QualityThresholds, run_quality_gate
from census_agent.eval.harness import load_cases, run_eval


def test_quality_gate_deterministic() -> None:
    gate = run_quality_gate()
    assert gate.summary["golden"]["total"] > 0
    assert gate.summary["golden"]["passed"] >= QualityThresholds().min_golden_passed - 1


@pytest.mark.e2e
def test_phase5_llm_regression(require_gemini: None) -> None:
    settings = get_settings()
    if not settings.embedding_index_path.exists():
        pytest.skip("field index missing")

    llm_cases = [
        c
        for c in load_cases(settings.project_root / "evals" / "phase4_degradation.jsonl")
        if c.get("requires_llm")
    ]
    report = run_eval(llm_cases, settings)
    assert all(r.passed for r in report.results)
