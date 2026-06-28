"""Agent pipeline tests (deterministic, no LLM)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import duckdb
import pytest

from census_agent.agent.orchestrator import CensusAgent
from census_agent.config import Settings
from census_agent.guardrails.input import IntentClass, classify_input


def _mini_db(path: Path) -> None:
    conn = duckdb.connect(str(path))
    conn.execute('CREATE TABLE "2019_METADATA_CBG_FIPS_CODES" (STATE VARCHAR, STATE_FIPS VARCHAR, COUNTY VARCHAR, COUNTY_FIPS VARCHAR)')
    conn.execute("INSERT INTO \"2019_METADATA_CBG_FIPS_CODES\" VALUES ('CA','06','Santa Clara County','085'), ('TX','48','Travis County','453')")
    conn.execute('CREATE TABLE "2019_CBG_B01" (CENSUS_BLOCK_GROUP VARCHAR, "B01003e1" VARCHAR, "B01002e1" VARCHAR)')
    conn.execute("INSERT INTO \"2019_CBG_B01\" VALUES ('060850001001','1000','35'), ('060850001002','2000','40'), ('480453001001','5000','30')")
    conn.execute('CREATE TABLE "2019_CBG_B19" (CENSUS_BLOCK_GROUP VARCHAR, "B19013e1" VARCHAR)')
    conn.execute("INSERT INTO \"2019_CBG_B19\" VALUES ('060850001001','80000'), ('480453001001','60000')")
    conn.execute('CREATE TABLE "2019_CBG_B23" (CENSUS_BLOCK_GROUP VARCHAR, "B23025e3" VARCHAR, "B23025e5" VARCHAR)')
    conn.execute("INSERT INTO \"2019_CBG_B23\" VALUES ('060850001001','100','5')")
    conn.execute('CREATE TABLE "2019_CBG_B25" (CENSUS_BLOCK_GROUP VARCHAR, "B25003e1" VARCHAR, "B25003e2" VARCHAR)')
    conn.execute('CREATE TABLE "2019_METADATA_CBG_FIELD_DESCRIPTIONS" (TABLE_ID VARCHAR, TABLE_NUMBER VARCHAR, TABLE_TITLE VARCHAR, TABLE_TOPICS VARCHAR, FIELD_LEVEL_1 VARCHAR, FIELD_LEVEL_2 VARCHAR, FIELD_LEVEL_3 VARCHAR, FIELD_LEVEL_4 VARCHAR, FIELD_LEVEL_5 VARCHAR)')
    conn.close()


@pytest.fixture
def agent_settings(tmp_path: Path) -> Settings:
    db = tmp_path / "mini.duckdb"
    _mini_db(db)
    return Settings(
        duckdb_path=db,
        data_backend="duckdb",
        census_year=2019,
        embedding_index_path=tmp_path / "no_index.json",
    )


def test_guardrail_off_topic() -> None:
    assert classify_input("What's the weather?") == IntentClass.OUT_OF_SCOPE


def test_agent_population_ca(agent_settings: Settings) -> None:
    with CensusAgent(settings=agent_settings) as agent:
        resp = agent.ask("What is the total population of California?")
    assert not resp.refused
    assert resp.rows
    assert float(resp.rows[0]["value"]) == 3000


def test_agent_refuses_poem(agent_settings: Settings) -> None:
    with CensusAgent(settings=agent_settings) as agent:
        resp = agent.ask("Write me a poem")
    assert resp.refused
