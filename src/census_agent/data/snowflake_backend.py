"""Snowflake read-only backend."""

from __future__ import annotations

from typing import Any

import snowflake.connector

from census_agent.config import Settings
from census_agent.data.gateway import DataGateway


class SnowflakeGateway(DataGateway):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        kwargs: dict[str, Any] = {
            "account": settings.snowflake_account,
            "user": settings.snowflake_user,
            "role": settings.snowflake_role,
            "warehouse": settings.snowflake_warehouse,
            "database": settings.snowflake_database,
            "schema": settings.snowflake_schema,
        }
        if settings.snowflake_authenticator:
            kwargs["authenticator"] = settings.snowflake_authenticator
        else:
            kwargs["password"] = settings.snowflake_password
        self._conn = snowflake.connector.connect(**kwargs)

    def execute(self, sql: str, params: tuple | dict | None = None) -> list[dict[str, Any]]:
        cur = self._conn.cursor()
        try:
            cur.execute(sql, params or {})
            if cur.description is None:
                return []
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        finally:
            cur.close()

    def close(self) -> None:
        self._conn.close()
