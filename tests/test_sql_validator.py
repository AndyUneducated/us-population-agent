"""SQL validator unit tests."""

from __future__ import annotations

import pytest

from census_agent.config import Settings
from census_agent.guardrails.sql_validator import validate_sql


@pytest.fixture
def settings(tmp_path):
    return Settings(
        census_year=2019,
        duckdb_path=tmp_path / "x.duckdb",
        data_backend="duckdb",
    )


def test_rejects_dml(settings: Settings) -> None:
    r = validate_sql("DELETE FROM \"2019_CBG_B01\"", settings)
    assert not r.ok


def test_accepts_select_and_adds_limit(settings: Settings) -> None:
    sql = 'SELECT SUM("B01003e1") FROM "2019_CBG_B01"'
    r = validate_sql(sql, settings)
    assert r.ok
    assert "LIMIT" in r.sql.upper()


def test_rejects_unknown_table(settings: Settings) -> None:
    r = validate_sql('SELECT * FROM "evil_table"', settings)
    assert not r.ok
