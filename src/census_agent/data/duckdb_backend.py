"""DuckDB local snapshot backend."""

from __future__ import annotations

from typing import Any

import duckdb

from census_agent.config import Settings
from census_agent.data.gateway import DataGateway


class DuckDBGateway(DataGateway):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        if not settings.duckdb_path.exists():
            raise FileNotFoundError(
                f"DuckDB snapshot not found at {settings.duckdb_path}. "
                "Run: python scripts/etl_snapshot.py"
            )
        self._conn = duckdb.connect(str(settings.duckdb_path), read_only=True)

    def execute(self, sql: str, params: tuple | dict | None = None) -> list[dict[str, Any]]:
        cur = self._conn.execute(sql, params or {})
        if cur.description is None:
            return []
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def close(self) -> None:
        self._conn.close()
