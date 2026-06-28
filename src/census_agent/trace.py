"""Lightweight request trace for pipeline observability."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TraceEvent:
    stage: str
    detail: dict[str, Any] = field(default_factory=dict)
    elapsed_ms: float = 0.0


@dataclass
class Trace:
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    events: list[TraceEvent] = field(default_factory=list)
    started_at: float = field(default_factory=time.perf_counter)

    def record(self, stage: str, **detail: Any) -> None:
        elapsed = (time.perf_counter() - self.started_at) * 1000
        self.events.append(TraceEvent(stage=stage, detail=detail, elapsed_ms=elapsed))

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "events": [asdict(e) for e in self.events],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)
