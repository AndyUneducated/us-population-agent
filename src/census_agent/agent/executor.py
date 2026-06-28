"""SQL execution with timeout."""

from __future__ import annotations

import signal
from contextlib import contextmanager
from typing import Any, Iterator

from census_agent.config import Settings, get_settings
from census_agent.data.gateway import DataGateway


class QueryTimeoutError(TimeoutError):
    pass


@contextmanager
def _time_limit(seconds: int) -> Iterator[None]:
    def handler(signum, frame):  # noqa: ARG001
        raise QueryTimeoutError(f"Query exceeded {seconds}s timeout")

    if hasattr(signal, "SIGALRM"):
        old = signal.signal(signal.SIGALRM, handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old)
    else:
        yield


class QueryExecutor:
    def __init__(self, gateway: DataGateway, settings: Settings | None = None) -> None:
        self._gateway = gateway
        self._settings = settings or get_settings()

    def run(self, sql: str) -> list[dict[str, Any]]:
        timeout = self._settings.query_timeout_seconds
        try:
            with _time_limit(timeout):
                return self._gateway.execute(sql)
        except QueryTimeoutError:
            raise
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}") from e
