"""Unified read-only query interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from census_agent.config import Settings, get_settings


class DataGateway(ABC):
    """Abstract read-only SQL gateway."""

    @abstractmethod
    def execute(self, sql: str, params: tuple | dict | None = None) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    def __enter__(self) -> DataGateway:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def get_data_gateway(settings: Settings | None = None) -> DataGateway:
    settings = settings or get_settings()
    if settings.data_backend == "snowflake":
        from census_agent.data.snowflake_backend import SnowflakeGateway

        return SnowflakeGateway(settings)
    from census_agent.data.duckdb_backend import DuckDBGateway

    return DuckDBGateway(settings)
