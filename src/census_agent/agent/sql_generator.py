"""LLM-based SQL generation fallback."""

from __future__ import annotations

import re

from census_agent.config import Settings, get_settings
from census_agent.llm.chat import ChatClient
from census_agent.semantic.catalog import FieldInfo


def _extract_sql(text: str) -> str:
    match = re.search(r"```sql\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"(SELECT\b.*)", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip().rstrip(";")
    return text.strip()


def generate_sql_llm(
    question: str,
    fields: list[FieldInfo],
    settings: Settings | None = None,
) -> str:
    settings = settings or get_settings()
    field_lines = "\n".join(
        f"- {f.physical_table}.{f.column_name}: {f.table_title} — {f.description}"
        for f in fields[:8]
    )
    tables = sorted({f.physical_table for f in fields})
    system = (
        "You write DuckDB SQL for US Census ACS data at census block group granularity. "
        "Return ONLY one SELECT statement in a ```sql``` fenced block. "
        "Use quoted table and column identifiers. Join FIPS metadata for state/county names. "
        "Never use DML/DDL. Always aggregate appropriately."
    )
    user = f"""
Question: {question}

Allowed tables: {', '.join(tables)}
Candidate columns:
{field_lines}

FIPS table: "{settings.metadata_table('FIPS_CODES')}" with STATE, STATE_FIPS, COUNTY, COUNTY_FIPS.
Join: LEFT(d.CENSUS_BLOCK_GROUP,2)=f.STATE_FIPS AND SUBSTR(d.CENSUS_BLOCK_GROUP,3,3)=f.COUNTY_FIPS
"""
    client = ChatClient(settings, model=settings.ollama_model_main)
    raw = client.complete(system, user)
    return _extract_sql(raw)
