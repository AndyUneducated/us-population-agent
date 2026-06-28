"""Shared pytest fixtures."""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pytest

from census_agent.config import Settings


def gemini_api_available() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY", "").strip())


@pytest.fixture(scope="session")
def gemini_available() -> bool:
    return gemini_api_available()


@pytest.fixture
def require_gemini(gemini_available: bool) -> None:
    if not gemini_available:
        pytest.skip("GEMINI_API_KEY not set")


def _mini_db(path: Path) -> None:
    conn = duckdb.connect(str(path))
    conn.execute(
        'CREATE TABLE "2019_METADATA_CBG_FIPS_CODES" '
        "(STATE VARCHAR, STATE_FIPS VARCHAR, COUNTY VARCHAR, COUNTY_FIPS VARCHAR)"
    )
    conn.execute(
        """
        INSERT INTO "2019_METADATA_CBG_FIPS_CODES" VALUES
        ('CA','06','Santa Clara County','085'),
        ('TX','48','Travis County','453'),
        ('FL','12','Miami-Dade County','086'),
        ('WA','53','King County','033'),
        ('OR','41','Multnomah County','051'),
        ('NY','36','New York County','061')
        """
    )
    conn.execute(
        'CREATE TABLE "2019_CBG_B01" '
        '(CENSUS_BLOCK_GROUP VARCHAR, "B01003e1" VARCHAR, "B01002e1" VARCHAR)'
    )
    conn.execute(
        """
        INSERT INTO "2019_CBG_B01" VALUES
        ('060850001001','1000','35'),
        ('060850001002','2000','40'),
        ('484530001001','5000','30'),
        ('120860001001','3000','33'),
        ('530330001001','2500','34'),
        ('410510001001','1800','36'),
        ('360610001001','4000','32')
        """
    )
    conn.execute(
        'CREATE TABLE "2019_CBG_B19" (CENSUS_BLOCK_GROUP VARCHAR, "B19013e1" VARCHAR)'
    )
    conn.execute(
        """
        INSERT INTO "2019_CBG_B19" VALUES
        ('060850001001','80000'),
        ('484530001001','60000'),
        ('120860001001','55000'),
        ('530330001001','90000'),
        ('410510001001','70000'),
        ('360610001001','75000')
        """
    )
    conn.execute(
        'CREATE TABLE "2019_CBG_B23" '
        '(CENSUS_BLOCK_GROUP VARCHAR, "B23025e3" VARCHAR, "B23025e5" VARCHAR)'
    )
    conn.execute("INSERT INTO \"2019_CBG_B23\" VALUES ('060850001001','100','5'), ('120860001001','80','4')")
    conn.execute(
        'CREATE TABLE "2019_CBG_B25" '
        '(CENSUS_BLOCK_GROUP VARCHAR, "B25003e1" VARCHAR, "B25003e2" VARCHAR)'
    )
    conn.execute(
        """
        INSERT INTO "2019_CBG_B25" VALUES
        ('060850001001','100','60'),
        ('484530001001','100','55'),
        ('120860001001','100','65')
        """
    )
    conn.execute(
        'CREATE TABLE "2019_METADATA_CBG_FIELD_DESCRIPTIONS" '
        "(TABLE_ID VARCHAR, TABLE_NUMBER VARCHAR, TABLE_TITLE VARCHAR, TABLE_TOPICS VARCHAR, "
        "FIELD_LEVEL_1 VARCHAR, FIELD_LEVEL_2 VARCHAR, FIELD_LEVEL_3 VARCHAR, "
        "FIELD_LEVEL_4 VARCHAR, FIELD_LEVEL_5 VARCHAR)"
    )
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
