"""Grounded answer synthesis from query results."""

from __future__ import annotations

from typing import Any

from census_agent.config import Settings, get_settings


def _format_number(value: Any) -> str:
    if value is None:
        return "N/A"
    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(num) >= 1_000_000:
        return f"{num:,.0f}"
    if abs(num) >= 100:
        return f"{num:,.0f}"
    return f"{num:,.2f}"


def synthesize_answer(
    question: str,
    sql: str,
    rows: list[dict[str, Any]],
    settings: Settings | None = None,
) -> str:
    settings = settings or get_settings()
    if not rows:
        return (
            "I couldn't find census data matching your question. "
            "The region or metric may not be available in the dataset, "
            "or the block-group level data aggregates to no values for that filter."
        )

    row = rows[0]
    region = row.get("region", "the selected area")
    metric = row.get("metric", "the requested metric")
    value = row.get("value")

    year = settings.census_year
    answer = (
        f"Based on {year} ACS 5-year estimates at the census block group level, "
        f"**{metric}** for **{region}** is approximately **{_format_number(value)}**."
    )
    if "income" in str(metric).lower():
        answer += " (Inflation-adjusted dollars.)"
    if "%" in str(metric):
        answer += " This is a population-weighted rate aggregated across block groups."
    answer += (
        f"\n\n*Source: US Open Census data, vintage {year}. "
        f"Estimates are sums/medians across census block groups; "
        f"margin of error not shown.*"
    )
    return answer
