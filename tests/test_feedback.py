"""Feedback persistence tests."""

from __future__ import annotations

import json

from census_agent.config import Settings
from census_agent.feedback import feedback_path, save_feedback


def test_save_feedback_appends_jsonl(tmp_path) -> None:
    settings = Settings(
        data_dir=tmp_path,
        data_backend="duckdb",
        duckdb_path=tmp_path / "x.duckdb",
        census_year=2019,
    )
    path, seq = save_feedback(
        message_index=1,
        rating="up",
        question="population of CA?",
        answer="39 million",
        sql="SELECT 1",
        trace_id="abc123",
        settings=settings,
    )
    assert path == feedback_path(settings)
    assert seq == 1
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["rating"] == "up"
    assert row["question"] == "population of CA?"
    assert row["trace_id"] == "abc123"
