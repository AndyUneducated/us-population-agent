"""Evaluation harness over golden dataset."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from census_agent.agent.orchestrator import CensusAgent
from census_agent.agent.rewriter import Message
from census_agent.config import Settings, get_settings
from census_agent.guardrails.faithfulness import check_faithfulness


@dataclass
class EvalCaseResult:
    case_id: str
    question: str
    passed: bool
    reason: str
    latency_ms: float
    refused: bool = False
    has_number: bool = False
    faithful: bool | None = None
    failure_mode: str | None = None


@dataclass
class EvalReport:
    results: list[EvalCaseResult] = field(default_factory=list)

    def summary(self) -> dict:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        faithful_cases = [r for r in self.results if r.faithful is not None]
        faithful_ok = sum(1 for r in faithful_cases if r.faithful)
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total, 3) if total else 0,
            "faithfulness_rate": round(faithful_ok / len(faithful_cases), 3)
            if faithful_cases
            else None,
            "avg_latency_ms": round(
                sum(r.latency_ms for r in self.results) / total, 1
            )
            if total
            else 0,
        }


def _has_number(text: str) -> bool:
    return bool(re.search(r"\d[\d,]*", text))


def load_cases(path: Path) -> list[dict]:
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            cases.append(json.loads(line))
    return cases


def load_golden(path: Path | None = None) -> list[dict]:
    path = path or get_settings().project_root / "evals" / "golden.jsonl"
    return load_cases(path)


def _evaluate_case(case: dict, resp) -> tuple[bool, str]:
    expect = case.get("expect_type", "has_number")
    if expect == "refuse":
        passed = resp.refused
        return passed, "refused" if passed else "should have refused"
    if expect == "graceful_no_data":
        passed = not resp.refused and (
            resp.error is not None
            or "couldn't" in resp.answer.lower()
            or "not available" in resp.answer.lower()
            or "identify" in resp.answer.lower()
            or "block group" in resp.answer.lower()
            or "good-faith" in resp.answer.lower()
        )
        return passed, "graceful degradation" if passed else f"unexpected: {resp.answer[:80]}"
    if expect == "executed":
        passed = bool(resp.sql) and not resp.refused and resp.error is None
        return passed, "llm path executed" if passed else (resp.error or "no sql")
    if expect == "has_number_or_disclaimer":
        passed = (
            _has_number(resp.answer) or "ambiguous" in resp.answer.lower()
        ) and not resp.refused
        return passed, "number or disclaimer" if passed else resp.answer[:100]
    if expect == "has_number":
        passed = _has_number(resp.answer) and not resp.refused and resp.error is None
        if passed and case.get("expect_region"):
            region = case["expect_region"]
            passed = region in (resp.sql or "") or region in resp.answer
        if passed and case.get("expect_regions"):
            haystack = (resp.sql or "") + " " + resp.answer
            missing = [r for r in case["expect_regions"] if r not in haystack]
            passed = not missing
        if passed and case.get("expect_county"):
            passed = case["expect_county"].lower() in resp.answer.lower()
        return passed, "has grounded number" if passed else (resp.error or resp.answer[:100])
    return False, f"unknown expect_type {expect}"


def run_eval(
    cases: list[dict] | None = None,
    settings: Settings | None = None,
    *,
    case_filter: str | None = None,
) -> EvalReport:
    settings = settings or get_settings()
    cases = cases or load_golden()
    if case_filter == "llm_only":
        cases = [c for c in cases if c.get("requires_llm")]
    elif case_filter == "no_llm":
        cases = [c for c in cases if not c.get("requires_llm")]

    report = EvalReport()
    for case in cases:
        with CensusAgent(settings=settings) as agent:
            history = [
                Message(role=m["role"], content=m["content"])
                for m in case.get("history", [])
            ]
            t0 = time.perf_counter()
            resp = agent.ask(case["question"], history=history)
            latency = (time.perf_counter() - t0) * 1000

            passed, reason = _evaluate_case(case, resp)

            if passed and case.get("expect_faithful") and resp.rows:
                ok, faith_reason = check_faithfulness(resp.answer, resp.rows)
                if not ok:
                    passed = False
                    reason = f"faithfulness failed: {faith_reason}"

            if passed and "expect_failure_mode" in case:
                expected_fm = case["expect_failure_mode"]
                actual = resp.failure_mode or resp.error
                if actual != expected_fm:
                    passed = False
                    reason = f"expected failure_mode {expected_fm}, got {actual}"

            faithful = resp.faithful
            if faithful is None and resp.rows and not resp.refused and resp.error is None:
                faithful, _ = check_faithfulness(resp.answer, resp.rows)

            report.results.append(
                EvalCaseResult(
                    case_id=case["id"],
                    question=case["question"],
                    passed=passed,
                    reason=reason,
                    latency_ms=latency,
                    refused=resp.refused,
                    has_number=_has_number(resp.answer),
                    faithful=faithful,
                    failure_mode=resp.failure_mode,
                )
            )

    return report
