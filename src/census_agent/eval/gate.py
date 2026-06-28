"""Quality gate thresholds for regression evals."""

from __future__ import annotations

from dataclasses import dataclass, field

from census_agent.eval.harness import EvalReport, load_cases, run_eval
from census_agent.config import Settings, get_settings
from pathlib import Path


@dataclass(frozen=True)
class QualityThresholds:
    min_pass_rate: float = 0.85
    min_faithfulness_rate: float = 0.9
    max_avg_latency_ms: float = 60_000.0
    min_golden_passed: int = 8


@dataclass
class GateResult:
    passed: bool
    summary: dict
    violations: list[str] = field(default_factory=list)


def run_quality_gate(
    *,
    golden_path: Path | None = None,
    degradation_path: Path | None = None,
    settings: Settings | None = None,
    thresholds: QualityThresholds | None = None,
) -> GateResult:
    settings = settings or get_settings()
    thresholds = thresholds or QualityThresholds()
    root = settings.project_root

    golden_path = golden_path or root / "evals" / "golden.jsonl"
    degradation_path = degradation_path or root / "evals" / "phase4_degradation.jsonl"

    golden_report = run_eval(load_cases(golden_path), settings)
    degradation_report = run_eval(
        [c for c in load_cases(degradation_path) if not c.get("requires_llm")],
        settings,
    )

    violations: list[str] = []
    g_sum = golden_report.summary()
    d_sum = degradation_report.summary()

    if g_sum["passed"] < thresholds.min_golden_passed:
        violations.append(
            f"golden passed {g_sum['passed']}/{g_sum['total']} < {thresholds.min_golden_passed}"
        )
    if g_sum["pass_rate"] < thresholds.min_pass_rate:
        violations.append(f"golden pass_rate {g_sum['pass_rate']} < {thresholds.min_pass_rate}")
    if g_sum.get("faithfulness_rate") is not None:
        if g_sum["faithfulness_rate"] < thresholds.min_faithfulness_rate:
            violations.append(
                f"faithfulness {g_sum['faithfulness_rate']} < {thresholds.min_faithfulness_rate}"
            )
    if g_sum["avg_latency_ms"] > thresholds.max_avg_latency_ms:
        violations.append(
            f"avg latency {g_sum['avg_latency_ms']}ms > {thresholds.max_avg_latency_ms}ms"
        )
    if d_sum["pass_rate"] < 0.75:
        violations.append(f"degradation pass_rate {d_sum['pass_rate']} < 0.75")

    return GateResult(
        passed=not violations,
        summary={
            "golden": g_sum,
            "degradation": d_sum,
        },
        violations=violations,
    )
