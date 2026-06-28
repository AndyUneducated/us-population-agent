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


def _row_get(row: dict[str, Any], key: str, default: str = "") -> Any:
    if key in row:
        return row[key]
    upper = key.upper()
    if upper in row:
        return row[upper]
    return default


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

    year = settings.census_year

    if len(rows) > 1:
        return _synthesize_comparison(rows, year)

    row = rows[0]
    region = _row_get(row, "region", "the selected area")
    metric = _row_get(row, "metric", "the requested metric")
    value = _row_get(row, "value")

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


def _synthesize_comparison(rows: list[dict[str, Any]], year: int) -> str:
    """Compare a metric across multiple regions (rows ordered by value desc)."""
    metric = _row_get(rows[0], "metric", "the requested metric")
    is_pct = "%" in str(metric)
    is_income = "income" in str(metric).lower()

    lines = []
    for row in rows:
        region = _row_get(row, "region", "?")
        value = _row_get(row, "value")
        lines.append(f"- **{region}**: {_format_number(value)}")

    answer = (
        f"Based on {year} ACS 5-year estimates at the census block group level, "
        f"here is **{metric}** across the regions you asked about:\n\n" + "\n".join(lines)
    )

    try:
        top = rows[0]
        bottom = rows[-1]
        top_val = float(_row_get(top, "value"))
        bottom_val = float(_row_get(bottom, "value"))
        diff = top_val - bottom_val
        top_region = _row_get(top, "region", "?")
        bottom_region = _row_get(bottom, "region", "?")
        unit = " percentage points" if is_pct else ""
        answer += (
            f"\n\n**{top_region}** is the highest and **{bottom_region}** the lowest, "
            f"a gap of about **{_format_number(diff)}{unit}**"
        )
        if not is_pct and bottom_val:
            ratio = top_val / bottom_val
            answer += f" (≈{ratio:.1f}× larger)"
        answer += "."
    except (TypeError, ValueError, ZeroDivisionError):
        pass

    if is_income:
        answer += " (Inflation-adjusted dollars.)"
    if is_pct:
        answer += " Rates are population-weighted across block groups."

    answer += (
        f"\n\n*Source: US Open Census data, vintage {year}. "
        f"Estimates are sums/medians across census block groups; "
        f"margin of error not shown.*"
    )
    return answer
