"""Query executor tests."""

from __future__ import annotations

import threading
from pathlib import Path

import duckdb
import pytest

from census_agent.agent.executor import QueryExecutor
from census_agent.config import Settings
from census_agent.data.duckdb_backend import DuckDBGateway


@pytest.fixture
def gateway(tmp_path: Path) -> DuckDBGateway:
    db = tmp_path / "t.duckdb"
    conn = duckdb.connect(str(db))
    conn.execute('CREATE TABLE "2019_CBG_B01" (CENSUS_BLOCK_GROUP VARCHAR, "B01003e1" VARCHAR)')
    conn.execute("INSERT INTO \"2019_CBG_B01\" VALUES ('010010201001', '100')")
    conn.close()
    settings = Settings(duckdb_path=db, data_backend="duckdb", census_year=2019)
    return DuckDBGateway(settings)


def test_executor_runs_in_worker_thread(gateway: DuckDBGateway) -> None:
    """Streamlit invokes handlers off the main thread; must not use SIGALRM."""
    executor = QueryExecutor(gateway)
    result: list = []
    error: list[BaseException] = []

    def worker() -> None:
        try:
            result.append(
                executor.run('SELECT SUM(CAST("B01003e1" AS DOUBLE)) AS v FROM "2019_CBG_B01"')
            )
        except BaseException as e:
            error.append(e)

    t = threading.Thread(target=worker)
    t.start()
    t.join(timeout=5)
    assert not error, error
    assert result[0][0]["v"] == 100.0
    gateway.close()
