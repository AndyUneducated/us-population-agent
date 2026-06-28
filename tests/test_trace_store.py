"""Trace persistence tests."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb

from census_agent.agent.orchestrator import CensusAgent
from census_agent.config import Settings
from census_agent.observability.trace_store import trace_log_path


def _mini_db(path: Path) -> None:
    conn = duckdb.connect(str(path))
    conn.execute(
        'CREATE TABLE "2019_METADATA_CBG_FIPS_CODES" '
        "(STATE VARCHAR, STATE_FIPS VARCHAR, COUNTY VARCHAR, COUNTY_FIPS VARCHAR)"
    )
    conn.execute(
        "INSERT INTO \"2019_METADATA_CBG_FIPS_CODES\" VALUES "
        "('CA','06','Santa Clara County','085'), ('TX','48','Travis County','453')"
    )
    conn.execute(
        'CREATE TABLE "2019_CBG_B01" '
        '(CENSUS_BLOCK_GROUP VARCHAR, "B01003e1" VARCHAR, "B01002e1" VARCHAR)'
    )
    conn.execute(
        "INSERT INTO \"2019_CBG_B01\" VALUES "
        "('060850001001','1000','35'), ('060850001002','2000','40'), ('480453001001','5000','30')"
    )
    conn.execute(
        'CREATE TABLE "2019_CBG_B19" (CENSUS_BLOCK_GROUP VARCHAR, "B19013e1" VARCHAR)'
    )
    conn.execute(
        "INSERT INTO \"2019_CBG_B19\" VALUES ('060850001001','80000'), ('480453001001','60000')"
    )
    conn.execute(
        'CREATE TABLE "2019_CBG_B23" '
        '(CENSUS_BLOCK_GROUP VARCHAR, "B23025e3" VARCHAR, "B23025e5" VARCHAR)'
    )
    conn.execute("INSERT INTO \"2019_CBG_B23\" VALUES ('060850001001','100','5')")
    conn.execute(
        'CREATE TABLE "2019_CBG_B25" '
        '(CENSUS_BLOCK_GROUP VARCHAR, "B25003e1" VARCHAR, "B25003e2" VARCHAR)'
    )
    conn.execute(
        'CREATE TABLE "2019_METADATA_CBG_FIELD_DESCRIPTIONS" '
        "(TABLE_ID VARCHAR, TABLE_NUMBER VARCHAR, TABLE_TITLE VARCHAR, TABLE_TOPICS VARCHAR, "
        "FIELD_LEVEL_1 VARCHAR, FIELD_LEVEL_2 VARCHAR, FIELD_LEVEL_3 VARCHAR, "
        "FIELD_LEVEL_4 VARCHAR, FIELD_LEVEL_5 VARCHAR)"
    )
    conn.close()


def test_trace_persisted_on_ask(tmp_path) -> None:
    db = tmp_path / "mini.duckdb"
    _mini_db(db)
    settings = Settings(
        duckdb_path=db,
        data_backend="duckdb",
        census_year=2019,
        data_dir=tmp_path / "data",
        embedding_index_path=tmp_path / "no_index.json",
    )
    log = trace_log_path(settings)
    assert not log.exists()

    with CensusAgent(settings=settings) as agent:
        agent.ask("What is the total population of California?")

    assert log.exists()
    lines = log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["question"]
    assert record["trace_id"]
    assert record["events"]
