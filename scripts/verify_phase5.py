#!/usr/bin/env python3
"""Phase 5 acceptance: quality gate + model-calling regression E2E."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from census_agent.config import get_settings
from census_agent.eval.gate import QualityThresholds, run_quality_gate
from census_agent.eval.harness import load_cases, run_eval


def gemini_available() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY", "").strip())


def main() -> int:
    settings = get_settings()
    errors: list[str] = []

    gate = run_quality_gate(settings=settings)
    g = gate.summary["golden"]
    d = gate.summary["degradation"]
    print(f"Golden: {g['passed']}/{g['total']} pass_rate={g['pass_rate']} faith={g.get('faithfulness_rate')}")
    print(f"Degradation (det): {d['passed']}/{d['total']} pass_rate={d['pass_rate']}")
    if gate.violations:
        for v in gate.violations:
            print(f"  GATE: {v}")
            errors.append(v)

    if g["pass_rate"] < QualityThresholds().min_pass_rate:
        errors.append("golden below min pass rate")

    if gemini_available() and settings.embedding_index_path.exists():
        llm_cases = [
            c
            for c in load_cases(ROOT / "evals" / "phase4_degradation.jsonl")
            if c.get("requires_llm")
        ]
        llm_report = run_eval(llm_cases, settings)
        ls = llm_report.summary()
        print(f"\nLLM regression: {ls['passed']}/{ls['total']} passed")
        for r in llm_report.results:
            status = "OK" if r.passed else "FAIL"
            faith = "faithful" if r.faithful else ("unfaithful" if r.faithful is False else "n/a")
            print(f"  {status} {r.case_id} [{faith}]: {r.reason}")
            if not r.passed:
                errors.append(f"llm regression {r.case_id}: {r.reason}")
    else:
        print("\nSKIP LLM regression (Gemini API key or field index unavailable)")
        errors.append("gemini api key + field index required for phase 5 LLM regression")

    if errors:
        print("\nPhase 5 FAILED:")
        for e in errors:
            print(" -", e)
        return 1
    print("\nPhase 5 acceptance: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
