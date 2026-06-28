"""SQL validation guardrails."""

from __future__ import annotations

import re
from dataclasses import dataclass

import sqlglot
from sqlglot import exp

from census_agent.config import Settings, get_settings


@dataclass
class SqlValidationResult:
    ok: bool
    sql: str
    error: str | None = None


FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|MERGE|TRUNCATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


def _allowed_tables(settings: Settings) -> set[str]:
    suffixes = ("B01", "B02", "B03", "B15", "B19", "B23", "B25")
    tables = {settings.metadata_table("FIELD_DESCRIPTIONS"), settings.metadata_table("FIPS_CODES")}
    tables |= {settings.table_name(s) for s in suffixes}
    return tables


def validate_sql(sql: str, settings: Settings | None = None) -> SqlValidationResult:
    settings = settings or get_settings()
    cleaned = sql.strip().rstrip(";")

    if FORBIDDEN.search(cleaned):
        return SqlValidationResult(False, cleaned, "Only SELECT queries are allowed.")

    try:
        statements = sqlglot.parse(cleaned, read="duckdb")
    except Exception as e:
        return SqlValidationResult(False, cleaned, f"SQL parse error: {e}")

    if len(statements) != 1:
        return SqlValidationResult(False, cleaned, "Exactly one SQL statement is required.")

    stmt = statements[0]
    if not isinstance(stmt, exp.Select):
        return SqlValidationResult(False, cleaned, "Only SELECT statements are allowed.")

    allowed = _allowed_tables(settings)
    for table in stmt.find_all(exp.Table):
        name = table.name
        if name not in allowed:
            return SqlValidationResult(False, cleaned, f"Table not allowed: {name}")

    if not stmt.find(exp.Limit):
        cleaned = f"{cleaned}\nLIMIT {settings.sql_row_limit}"

    return SqlValidationResult(True, cleaned, None)
