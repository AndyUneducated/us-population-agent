"""Persist user feedback from the chat UI."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from census_agent.config import Settings, get_settings


def feedback_path(settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    path = settings.data_dir / "feedback.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def count_feedback(settings: Settings | None = None) -> int:
    path = feedback_path(settings)
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def save_feedback(
    *,
    message_index: int,
    rating: str,
    question: str,
    answer: str,
    sql: str | None = None,
    trace_id: str | None = None,
    settings: Settings | None = None,
) -> tuple[Path, int]:
    """Append feedback and return (path, 1-based sequence number in the log file)."""
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message_index": message_index,
        "rating": rating,
        "question": question,
        "answer": answer,
        "sql": sql,
        "trace_id": trace_id,
    }
    path = feedback_path(settings)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path, count_feedback(settings)
