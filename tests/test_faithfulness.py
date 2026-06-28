"""Faithfulness guardrail tests."""

from __future__ import annotations

from census_agent.guardrails.faithfulness import check_faithfulness


def test_faithfulness_grounded() -> None:
    rows = [{"region": "CA", "metric": "Population", "value": 39538223}]
    answer = "Population for CA is approximately **39,538,223**."
    ok, reason = check_faithfulness(answer, rows)
    assert ok, reason


def test_faithfulness_rounded_rate() -> None:
    rows = [{"region": "FL", "metric": "Owner-Occupied Housing Rate", "value": 65.39086911061358}]
    answer = "Owner-Occupied Housing Rate for FL is approximately **65.39**."
    ok, reason = check_faithfulness(answer, rows)
    assert ok, reason

    rows = [{"region": "CA", "metric": "Population", "value": 1000}]
    answer = "Population is **9,999,999**."
    ok, reason = check_faithfulness(answer, rows)
    assert not ok
    assert "ungrounded" in reason
