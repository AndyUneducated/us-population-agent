"""Configuration helpers."""

from __future__ import annotations

from pathlib import Path

import duckdb

from census_agent.config import Settings, resolve_census_year


def _make_snapshot(path: Path, year: int) -> None:
    conn = duckdb.connect(str(path))
    conn.execute(
        f'CREATE TABLE "{year}_METADATA_CBG_FIPS_CODES" '
        "(STATE VARCHAR, STATE_FIPS VARCHAR, COUNTY VARCHAR, COUNTY_FIPS VARCHAR)"
    )
    conn.close()


def test_resolve_census_year_prefers_configured_when_present(tmp_path: Path) -> None:
    db = tmp_path / "census.duckdb"
    _make_snapshot(db, 2019)
    _make_snapshot(db, 2020)

    settings = Settings(duckdb_path=db, data_backend="duckdb", census_year=2020)
    assert resolve_census_year(settings) == 2020


def test_resolve_census_year_falls_back_to_newest_duckdb_vintage(tmp_path: Path) -> None:
    db = tmp_path / "census.duckdb"
    _make_snapshot(db, 2019)

    settings = Settings(duckdb_path=db, data_backend="duckdb", census_year=2020)
    assert resolve_census_year(settings) == 2019


def test_resolve_census_year_keeps_snowflake_config(tmp_path: Path) -> None:
    settings = Settings(data_backend="snowflake", census_year=2020)
    assert resolve_census_year(settings) == 2020
