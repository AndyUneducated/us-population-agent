"""Data gateway tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

import duckdb
import pytest

from census_agent.config import Settings
from census_agent.data.duckdb_backend import DuckDBGateway


@pytest.fixture
def duckdb_settings(tmp_path: Path) -> Settings:
    db_path = tmp_path / "test.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.execute('CREATE TABLE "demo" (id INTEGER, name VARCHAR)')
    conn.execute("INSERT INTO demo VALUES (1, 'alpha'), (2, 'beta')")
    conn.close()
    return Settings(duckdb_path=db_path, data_backend="duckdb")


def test_duckdb_gateway_execute(duckdb_settings: Settings) -> None:
    with DuckDBGateway(duckdb_settings) as gw:
        rows = gw.execute('SELECT * FROM "demo" ORDER BY id')
    assert len(rows) == 2
    assert rows[0]["name"] == "alpha"
