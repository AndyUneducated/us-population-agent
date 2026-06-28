"""Deterministic SQL builder for curated metrics."""

from __future__ import annotations

from census_agent.config import Settings, get_settings
from census_agent.semantic.geo import GeoMatch
from census_agent.semantic.metrics import MetricDefinition


def _quote(identifier: str) -> str:
    return f'"{identifier}"'


def _metric_expr(metric: MetricDefinition) -> tuple[str, str]:
    """Return (SQL aggregate expression over alias d, display label)."""
    if metric.aggregation == "median":
        return f'MEDIAN(TRY_CAST(d.{_quote(metric.column)} AS DOUBLE))', metric.name
    if metric.aggregation == "ratio" and metric.ratio_numerator and metric.ratio_denominator:
        num = _quote(metric.ratio_numerator)
        den = _quote(metric.ratio_denominator)
        expr = (
            f"100.0 * SUM(TRY_CAST(d.{num} AS DOUBLE)) "
            f"/ NULLIF(SUM(TRY_CAST(d.{den} AS DOUBLE)), 0)"
        )
        return expr, metric.name + " (%)"
    return f'SUM(TRY_CAST(d.{_quote(metric.column)} AS DOUBLE))', metric.name


def _geo_join_and_filter(geo: GeoMatch | None, d_alias: str = "d") -> tuple[str, str]:
    fips = _quote(get_settings().metadata_table("FIPS_CODES"))
    if not geo:
        return "", ""
    join = (
        f' JOIN {fips} f ON LEFT({d_alias}.CENSUS_BLOCK_GROUP, 2) = f.STATE_FIPS'
        f" AND SUBSTR({d_alias}.CENSUS_BLOCK_GROUP, 3, 3) = f.COUNTY_FIPS"
    )
    if geo.county_fips:
        where = (
            f"f.STATE = '{geo.state}' AND f.COUNTY = '{geo.county}'"
        )
    else:
        where = f"f.STATE = '{geo.state}'"
    return join, where


def build_metric_sql(
    metric: MetricDefinition,
    geo: GeoMatch | None = None,
    settings: Settings | None = None,
) -> str:
    settings = settings or get_settings()
    table = _quote(settings.table_name(metric.table_suffix))
    join, where = _geo_join_and_filter(geo)
    expr, label = _metric_expr(metric)

    where_clause = f"WHERE {where}" if where else ""
    geo_label = geo.label if geo else "United States"
    return f"""
SELECT '{geo_label}' AS region, '{label}' AS metric, {expr} AS value
FROM {table} d
{join}
{where_clause}
""".strip()


def build_comparison_sql(
    metric: MetricDefinition,
    geos: list[GeoMatch],
    settings: Settings | None = None,
) -> str:
    """Multi-state comparison: one grouped row per state, ranked by value."""
    settings = settings or get_settings()
    table = _quote(settings.table_name(metric.table_suffix))
    fips = _quote(settings.metadata_table("FIPS_CODES"))
    expr, label = _metric_expr(metric)
    states = ", ".join(f"'{g.state}'" for g in geos)
    return f"""
SELECT f.STATE AS region, '{label}' AS metric, {expr} AS value
FROM {table} d
JOIN {fips} f ON LEFT(d.CENSUS_BLOCK_GROUP, 2) = f.STATE_FIPS
 AND SUBSTR(d.CENSUS_BLOCK_GROUP, 3, 3) = f.COUNTY_FIPS
WHERE f.STATE IN ({states})
GROUP BY f.STATE
ORDER BY value DESC
""".strip()
