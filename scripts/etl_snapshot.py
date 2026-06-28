#!/usr/bin/env python3
"""ETL: export census tables from Snowflake into a local DuckDB snapshot."""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from census_agent.config import get_settings
from census_agent.data.snowflake_backend import SnowflakeGateway
from census_agent.logging_setup import setup_logging

logger = setup_logging()

DATA_SUFFIXES = ("B01", "B02", "B03", "B15", "B19", "B23", "B25")
METADATA_TABLES = ("FIELD_DESCRIPTIONS", "FIPS_CODES")  # skip GEOGRAPHIC_DATA for faster snapshot
BATCH_SIZE = 10_000

# Subset wide tables to essential estimate columns for faster local snapshot
COLUMN_SUBSETS: dict[str, list[str]] = {
    "B01": [
        "CENSUS_BLOCK_GROUP",
        "B01001e1",
        "B01002e1",
        "B01003e1",
        "B01001e2",
        "B01001e26",
    ],
    "B19": [
        "CENSUS_BLOCK_GROUP",
        "B19001e1",
        "B19013e1",
        "B19025e1",
        "B19049e1",
    ],
    "B25": [
        "CENSUS_BLOCK_GROUP",
        "B25001e1",
        "B25003e1",
        "B25003e2",
        "B25003e3",
        "B25077e1",
    ],
    "B23": [
        "CENSUS_BLOCK_GROUP",
        "B23025e1",
        "B23025e2",
        "B23025e3",
        "B23025e4",
        "B23025e5",
        "B23025e7",
    ],
    "B15": [
        "CENSUS_BLOCK_GROUP",
        "B15003e1",
        "B15003e17",
        "B15003e18",
        "B15003e19",
        "B15003e22",
        "B15003e23",
    ],
}


def export_table(
    sf: SnowflakeGateway,
    duck: duckdb.DuckDBPyConnection,
    table: str,
    suffix: str | None = None,
) -> int:
    quoted = f'"{table}"'
    cols = None
    if suffix and suffix in COLUMN_SUBSETS:
        cols = COLUMN_SUBSETS[suffix]
    select = ", ".join(f'"{c}"' for c in cols) if cols else "*"
    logger.info("Exporting %s (%s) ...", table, select if cols else "all columns")
    cur = sf._conn.cursor()
    total = 0
    try:
        cur.execute(f"SELECT {select} FROM {quoted}")
        if cur.description is None:
            duck.execute(f'CREATE TABLE "{table}" AS SELECT * FROM (SELECT 1 WHERE false)')
            return 0
        cols = [d[0] for d in cur.description]
        col_defs = ", ".join(f'"{c}" VARCHAR' for c in cols)
        duck.execute(f'DROP TABLE IF EXISTS "{table}"')
        duck.execute(f'CREATE TABLE "{table}" ({col_defs})')
        placeholders = ", ".join("?" for _ in cols)
        insert_sql = f'INSERT INTO "{table}" VALUES ({placeholders})'
        while True:
            batch_rows = cur.fetchmany(BATCH_SIZE)
            if not batch_rows:
                break
            batch = [
                tuple(str(v) if v is not None else None for v in row)
                for row in batch_rows
            ]
            duck.executemany(insert_sql, batch)
            total += len(batch)
            if total % 50_000 == 0:
                logger.info("  ... %d rows", total)
    finally:
        cur.close()
    logger.info("  -> %d rows", total)
    return total


def main() -> int:
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    out = settings.duckdb_path
    if out.exists():
        out.unlink()

    tables = [settings.metadata_table(m) for m in METADATA_TABLES]
    data_tables = [(settings.table_name(s), s) for s in DATA_SUFFIXES]

    with SnowflakeGateway(settings) as sf:
        duck = duckdb.connect(str(out))
        try:
            for table in tables:
                export_table(sf, duck, table)
            for table, suffix in data_tables:
                export_table(sf, duck, table, suffix=suffix)
            logger.info("Snapshot written to %s", out)
        finally:
            duck.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
