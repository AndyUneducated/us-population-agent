"""SQL execution with optional timeout (Streamlit-safe)."""

from __future__ import annotations

import signal
import threading
from contextlib import contextmanager
from typing import Any, Iterator

from census_agent.config import Settings, get_settings
from census_agent.data.gateway import DataGateway, normalize_rows


class QueryTimeoutError(TimeoutError):
    pass


def _signal_timeout_available() -> bool:
    """SIGALRM only works on the main thread (breaks under Streamlit)."""
    return (
        hasattr(signal, "SIGALRM")
        and threading.current_thread() is threading.main_thread()
    )


@contextmanager
def _time_limit(seconds: int) -> Iterator[None]:
    if not _signal_timeout_available():
        yield
        return

    def handler(signum, frame):  # noqa: ARG001
        raise QueryTimeoutError(f"Query exceeded {seconds}s timeout")

    old = signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


class QueryExecutor:
    def __init__(self, gateway: DataGateway, settings: Settings | None = None) -> None:
        self._gateway = gateway
        self._settings = settings or get_settings()

    def run(self, sql: str) -> list[dict[str, Any]]:
        timeout = self._settings.query_timeout_seconds
        try:
            with _time_limit(timeout):
                return normalize_rows(self._gateway.execute(sql))
        except QueryTimeoutError:
            raise
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}") from e
