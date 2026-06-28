"""Curated metric definitions aligned with Cortex semantic model concepts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricDefinition:
    id: str
    name: str
    synonyms: tuple[str, ...]
    table_suffix: str
    column: str
    description: str
    aggregation: str = "sum"  # sum | median | ratio | none
    ratio_numerator: str | None = None
    ratio_denominator: str | None = None


METRICS: tuple[MetricDefinition, ...] = (
    MetricDefinition(
        id="total_population",
        name="Total Population",
        synonyms=("population", "residents", "people", "人口", "总人口"),
        table_suffix="B01",
        column="B01003e1",
        description="Total population (ACS estimate)",
        aggregation="sum",
    ),
    MetricDefinition(
        id="median_household_income",
        name="Median Household Income",
        synonyms=(
            "median income",
            "household income",
            "income",
            "中位收入",
            "家庭收入",
        ),
        table_suffix="B19",
        column="B19013e1",
        description="Median household income in the past 12 months (inflation-adjusted)",
        aggregation="median",
    ),
    MetricDefinition(
        id="median_age",
        name="Median Age",
        synonyms=("median age", "average age", "age", "中位年龄", "年龄"),
        table_suffix="B01",
        column="B01002e1",
        description="Median age of the population",
        aggregation="median",
    ),
    MetricDefinition(
        id="owner_occupied_rate",
        name="Owner-Occupied Housing Rate",
        synonyms=(
            "homeownership rate",
            "owner occupied",
            "housing ownership",
            "自有住房率",
            "住房自有率",
        ),
        table_suffix="B25",
        column="B25003e2",
        description="Owner-occupied housing units as a share of occupied units",
        aggregation="ratio",
        ratio_numerator="B25003e2",
        ratio_denominator="B25003e1",
    ),
    MetricDefinition(
        id="unemployment_rate",
        name="Unemployment Rate",
        synonyms=("unemployment", "jobless", "失业率", "失业"),
        table_suffix="B23",
        column="B23025e5",
        description="Unemployed civilians in labor force (numerator for rate)",
        aggregation="ratio",
        ratio_numerator="B23025e5",
        ratio_denominator="B23025e3",
    ),
    MetricDefinition(
        id="bachelors_degree_rate",
        name="Bachelor's Degree Rate",
        synonyms=("college degree", "bachelors", "本科学历", "大学学位"),
        table_suffix="B15",
        column="B15003e22",
        description="Population 25+ with bachelor's degree or higher (partial)",
        aggregation="sum",
    ),
)


def match_metric(query: str) -> MetricDefinition | None:
    """Fast-path: match query text to a curated metric."""
    q = query.lower()
    best: MetricDefinition | None = None
    best_len = 0
    for metric in METRICS:
        for term in (metric.name.lower(),) + metric.synonyms:
            t = term.lower()
            if t in q and len(t) > best_len:
                best = metric
                best_len = len(t)
    return best
