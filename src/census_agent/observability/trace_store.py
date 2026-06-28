"""Persist agent traces for debugging and eval feedback loops."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from census_agent.config import Settings, get_settings
from census_agent.trace import Trace


def trace_log_path(settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    path = settings.data_dir / "traces.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def append_trace(
    *,
    question: str,
    trace: Trace,
    answer: str,
    sql: str | None = None,
    error: str | None = None,
    refused: bool = False,
    settings: Settings | None = None,
) -> Path:
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": trace.trace_id,
        "question": question,
        "answer_preview": answer[:500],
        "sql": sql,
        "error": error,
        "refused": refused,
        "events": trace.to_dict()["events"],
    }
    path = trace_log_path(settings)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return path
