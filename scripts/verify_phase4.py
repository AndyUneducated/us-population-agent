#!/usr/bin/env python3
"""Phase 4 acceptance: degradation paths, trace persistence, model E2E."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from census_agent.agent.orchestrator import CensusAgent
from census_agent.config import get_settings
from census_agent.eval.harness import load_cases, run_eval
from census_agent.observability.trace_store import trace_log_path


def gemini_available() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY", "").strip())


def main() -> int:
    settings = get_settings()
    errors: list[str] = []

    cases_path = ROOT / "evals" / "phase4_degradation.jsonl"
    det_cases = [c for c in load_cases(cases_path) if not c.get("requires_llm")]
    report = run_eval(det_cases, settings)
    summary = report.summary()
    print(f"Degradation eval (deterministic): {summary['passed']}/{summary['total']} passed")
    for r in report.results:
        status = "OK" if r.passed else "FAIL"
        print(f"  {status} {r.case_id}: {r.reason} ({r.latency_ms:.0f}ms)")
        if not r.passed:
            errors.append(f"degradation {r.case_id}: {r.reason}")

    if summary["passed"] < max(1, summary["total"] - 1):
        errors.append(f"degradation pass rate too low: {summary['pass_rate']}")

    with CensusAgent(settings=settings) as agent:
        agent.ask("What is the weather today?")
    log = trace_log_path(settings)
    if not log.exists():
        errors.append("trace log not created")
    else:
        last = json.loads(log.read_text(encoding="utf-8").strip().splitlines()[-1])
        if not last.get("trace_id"):
            errors.append("trace missing trace_id")
        print(f"Trace log OK: {log} ({len(log.read_text().splitlines())} records)")

    if not gemini_available():
        print("\nSKIP LLM E2E: GEMINI_API_KEY not set")
        errors.append("gemini api key required for phase 4 LLM E2E")
    elif not settings.embedding_index_path.exists():
        print("\nSKIP LLM E2E: field index missing (run scripts/build_embeddings.py)")
        errors.append("field index required for LLM E2E")
    else:
        llm_cases = [c for c in load_cases(cases_path) if c.get("requires_llm")]
        llm_report = run_eval(llm_cases, settings)
        ls = llm_report.summary()
        print(f"\nLLM E2E eval: {ls['passed']}/{ls['total']} passed")
        for r in llm_report.results:
            status = "OK" if r.passed else "FAIL"
            print(f"  {status} {r.case_id}: {r.reason} ({r.latency_ms:.0f}ms)")
            if not r.passed:
                errors.append(f"llm e2e {r.case_id}: {r.reason}")

    if errors:
        print("\nPhase 4 FAILED:")
        for e in errors:
            print(" -", e)
        return 1
    print("\nPhase 4 acceptance: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
