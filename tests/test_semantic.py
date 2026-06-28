"""Phase 1 unit tests (no network required when DuckDB snapshot present)."""

from __future__ import annotations

import pytest

from census_agent.semantic.geo import GeoResolver, STATE_ALIASES
from census_agent.semantic.metrics import METRICS, match_metric


class FakeGateway:
    def __init__(self, fips_rows: list[dict]) -> None:
        self._fips = fips_rows

    def execute(self, sql: str, params=None):
        if "FIPS_CODES" in sql:
            return self._fips
        return []

    def close(self) -> None:
        pass


@pytest.mark.parametrize(
    "query,expected_id",
    [
        ("total population of CA", "total_population"),
        ("median household income", "median_household_income"),
        ("homeownership rate", "owner_occupied_rate"),
    ],
)
def test_match_metric(query: str, expected_id: str) -> None:
    m = match_metric(query)
    assert m is not None
    assert m.id == expected_id


def test_geo_state_resolution() -> None:
    gw = FakeGateway(
        [
            {"STATE": "CA", "STATE_FIPS": "06", "COUNTY": "Santa Clara County", "COUNTY_FIPS": "085"},
            {"STATE": "TX", "STATE_FIPS": "48", "COUNTY": "Travis County", "COUNTY_FIPS": "453"},
        ]
    )
    resolver = GeoResolver(gw)
    matches = resolver.resolve("population in California")
    assert len(matches) == 1
    assert matches[0].state == "CA"
    assert matches[0].state_fips == "06"


def test_geo_county_resolution() -> None:
    gw = FakeGateway(
        [
            {"STATE": "CA", "STATE_FIPS": "06", "COUNTY": "Santa Clara County", "COUNTY_FIPS": "085"},
        ]
    )
    resolver = GeoResolver(gw)
    matches = resolver.resolve("Santa Clara County income")
    assert len(matches) == 1
    assert matches[0].county == "Santa Clara County"
    assert matches[0].county_fips == "085"


def test_geo_new_york_prefers_state() -> None:
    gw = FakeGateway(
        [
            {"STATE": "NY", "STATE_FIPS": "36", "COUNTY": "New York County", "COUNTY_FIPS": "061"},
            {"STATE": "NY", "STATE_FIPS": "36", "COUNTY": "Kings County", "COUNTY_FIPS": "047"},
        ]
    )
    resolver = GeoResolver(gw)
    matches = resolver.resolve("How about New York?")
    assert len(matches) == 1
    assert matches[0].state == "NY"
    assert matches[0].county is None


def test_geo_oregon_not_indiana() -> None:
    gw = FakeGateway(
        [
            {"STATE": "OR", "STATE_FIPS": "41", "COUNTY": "Multnomah County", "COUNTY_FIPS": "051"},
            {"STATE": "IN", "STATE_FIPS": "18", "COUNTY": "Marion County", "COUNTY_FIPS": "097"},
        ]
    )
    resolver = GeoResolver(gw)
    matches = resolver.resolve("What about Oregon?")
    assert matches[0].state == "OR"


def test_metrics_catalog_not_empty() -> None:
    assert len(METRICS) >= 4
    assert STATE_ALIASES["california"] == "CA"
