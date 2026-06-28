"""State and county name resolution via FIPS codes."""

from __future__ import annotations

import re
from dataclasses import dataclass

from census_agent.config import Settings, get_settings
from census_agent.data.gateway import DataGateway, get_data_gateway


@dataclass(frozen=True)
class GeoMatch:
    state: str
    state_fips: str
    county: str | None
    county_fips: str | None

    @property
    def label(self) -> str:
        if self.county:
            return f"{self.county}, {self.state}"
        return self.state


# Common state aliases
STATE_ALIASES: dict[str, str] = {
    "california": "CA",
    "ca": "CA",
    "texas": "TX",
    "tx": "TX",
    "new york": "NY",
    "ny": "NY",
    "florida": "FL",
    "fl": "FL",
    "florida": "FL",
    "fl": "FL",
}


class GeoResolver:
    """Resolve natural language place names to FIPS-backed geo filters."""

    def __init__(self, gateway: DataGateway, settings: Settings | None = None) -> None:
        self._gateway = gateway
        self._settings = settings or get_settings()
        self._states: dict[str, str] = {}  # abbr -> fips
        self._counties: list[tuple[str, str, str, str]] = []  # state, state_fips, county, county_fips
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        table = self._settings.metadata_table("FIPS_CODES")
        rows = self._gateway.execute(f'SELECT STATE, STATE_FIPS, COUNTY, COUNTY_FIPS FROM "{table}"')
        seen_states: set[str] = set()
        for row in rows:
            st = str(row["STATE"]).strip()
            sf = str(row["STATE_FIPS"]).strip().zfill(2)
            county = str(row["COUNTY"]).strip()
            cf = str(row["COUNTY_FIPS"]).strip().zfill(3)
            if st not in seen_states:
                self._states[st.upper()] = sf
                seen_states.add(st)
            self._counties.append((st, sf, county, cf))
        self._loaded = True

    def resolve(self, text: str) -> list[GeoMatch]:
        self._load()
        text_lower = text.lower()
        matches: list[GeoMatch] = []

        # State detection
        state_abbr: str | None = None
        state_fips: str | None = None
        for alias, abbr in STATE_ALIASES.items():
            if re.search(rf"\b{re.escape(alias)}\b", text_lower):
                state_abbr = abbr
                state_fips = self._states.get(abbr)
                break
        if not state_abbr:
            for abbr, fips in self._states.items():
                if re.search(rf"\b{re.escape(abbr.lower())}\b", text_lower):
                    state_abbr = abbr
                    state_fips = fips
                    break

        # County detection (fuzzy substring)
        county_hit: tuple[str, str, str, str] | None = None
        for st, sf, county, cf in self._counties:
            county_lower = county.lower().replace(" county", "")
            if county_lower in text_lower or county.lower() in text_lower:
                if state_abbr and st != state_abbr:
                    continue
                county_hit = (st, sf, county, cf)
                break

        if county_hit:
            st, sf, county, cf = county_hit
            matches.append(GeoMatch(state=st, state_fips=sf, county=county, county_fips=cf))
        elif state_abbr and state_fips:
            matches.append(GeoMatch(state=state_abbr, state_fips=state_fips, county=None, county_fips=None))

        return matches

    def sql_filter(self, geo: GeoMatch, cbg_alias: str = "d") -> str:
        """Build SQL WHERE fragment filtering by state/county via CBG id prefix."""
        if geo.county_fips and geo.state_fips:
            prefix = f"{geo.state_fips}{geo.county_fips}"
            return f"LEFT({cbg_alias}.CENSUS_BLOCK_GROUP, 5) = '{prefix}'"
        if geo.state_fips:
            return f"LEFT({cbg_alias}.CENSUS_BLOCK_GROUP, 2) = '{geo.state_fips}'"
        return "1=1"


def get_geo_resolver(gateway: DataGateway | None = None) -> GeoResolver:
    gw = gateway or get_data_gateway()
    return GeoResolver(gw)
