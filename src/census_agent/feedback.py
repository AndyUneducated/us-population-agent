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


def save_feedback(
    *,
    message_index: int,
    rating: str,
    question: str,
    answer: str,
    sql: str | None = None,
    trace_id: str | None = None,
    settings: Settings | None = None,
) -> Path:
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
    return path
