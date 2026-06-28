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


@dataclass
class EvalCaseResult:
    case_id: str
    question: str
    passed: bool
    reason: str
    latency_ms: float
    refused: bool = False
    has_number: bool = False


@dataclass
class EvalReport:
    results: list[EvalCaseResult] = field(default_factory=list)

    def summary(self) -> dict:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total, 3) if total else 0,
            "avg_latency_ms": round(
                sum(r.latency_ms for r in self.results) / total, 1
            )
            if total
            else 0,
        }


def _has_number(text: str) -> bool:
    return bool(re.search(r"\d[\d,]*", text))


def load_golden(path: Path | None = None) -> list[dict]:
    path = path or get_settings().project_root / "evals" / "golden.jsonl"
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            cases.append(json.loads(line))
    return cases


def run_eval(
    cases: list[dict] | None = None,
    settings: Settings | None = None,
) -> EvalReport:
    settings = settings or get_settings()
    cases = cases or load_golden()
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

            expect = case.get("expect_type", "has_number")
            passed = False
            reason = ""

            if expect == "refuse":
                passed = resp.refused
                reason = "refused" if passed else "should have refused"
            elif expect == "graceful_no_data":
                passed = not resp.refused and (
                    resp.error is not None
                    or "couldn't" in resp.answer.lower()
                    or "not available" in resp.answer.lower()
                    or "identify" in resp.answer.lower()
                )
                reason = "graceful degradation" if passed else f"unexpected: {resp.answer[:80]}"
            elif expect == "has_number":
                passed = _has_number(resp.answer) and not resp.refused and resp.error is None
                if passed and case.get("expect_region"):
                    region = case["expect_region"]
                    passed = region in (resp.sql or "") or region in resp.answer
                if passed and case.get("expect_county"):
                    passed = case["expect_county"].lower() in resp.answer.lower()
                reason = "has grounded number" if passed else (resp.error or resp.answer[:100])
            else:
                reason = f"unknown expect_type {expect}"

            report.results.append(
                EvalCaseResult(
                    case_id=case["id"],
                    question=case["question"],
                    passed=passed,
                    reason=reason,
                    latency_ms=latency,
                    refused=resp.refused,
                    has_number=_has_number(resp.answer),
                )
            )

    return report
