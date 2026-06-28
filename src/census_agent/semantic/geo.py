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


# Full state names and common aliases → USPS abbreviation
STATE_ALIASES: dict[str, str] = {
    "alabama": "AL",
    "al": "AL",
    "alaska": "AK",
    "ak": "AK",
    "arizona": "AZ",
    "az": "AZ",
    "arkansas": "AR",
    "ar": "AR",
    "california": "CA",
    "ca": "CA",
    "colorado": "CO",
    "co": "CO",
    "connecticut": "CT",
    "ct": "CT",
    "delaware": "DE",
    "de": "DE",
    "florida": "FL",
    "fl": "FL",
    "georgia": "GA",
    "ga": "GA",
    "hawaii": "HI",
    "hi": "HI",
    "idaho": "ID",
    "id": "ID",
    "illinois": "IL",
    "il": "IL",
    "indiana": "IN",
    "in": "IN",
    "iowa": "IA",
    "ia": "IA",
    "kansas": "KS",
    "ks": "KS",
    "kentucky": "KY",
    "ky": "KY",
    "louisiana": "LA",
    "la": "LA",
    "maine": "ME",
    "me": "ME",
    "maryland": "MD",
    "md": "MD",
    "massachusetts": "MA",
    "ma": "MA",
    "michigan": "MI",
    "mi": "MI",
    "minnesota": "MN",
    "mn": "MN",
    "mississippi": "MS",
    "ms": "MS",
    "missouri": "MO",
    "mo": "MO",
    "montana": "MT",
    "mt": "MT",
    "nebraska": "NE",
    "ne": "NE",
    "nevada": "NV",
    "nv": "NV",
    "new hampshire": "NH",
    "nh": "NH",
    "new jersey": "NJ",
    "nj": "NJ",
    "new mexico": "NM",
    "nm": "NM",
    "new york": "NY",
    "ny": "NY",
    "north carolina": "NC",
    "nc": "NC",
    "north dakota": "ND",
    "nd": "ND",
    "ohio": "OH",
    "oh": "OH",
    "oklahoma": "OK",
    "ok": "OK",
    "oregon": "OR",
    "or": "OR",
    "pennsylvania": "PA",
    "pa": "PA",
    "rhode island": "RI",
    "ri": "RI",
    "south carolina": "SC",
    "sc": "SC",
    "south dakota": "SD",
    "sd": "SD",
    "tennessee": "TN",
    "tn": "TN",
    "texas": "TX",
    "tx": "TX",
    "utah": "UT",
    "ut": "UT",
    "vermont": "VT",
    "vt": "VT",
    "virginia": "VA",
    "va": "VA",
    "washington": "WA",
    "wa": "WA",
    "west virginia": "WV",
    "wv": "WV",
    "wisconsin": "WI",
    "wi": "WI",
    "wyoming": "WY",
    "wy": "WY",
    "district of columbia": "DC",
    "dc": "DC",
    "united states": "US",
    "usa": "US",
    "u.s.": "US",
    "nationwide": "US",
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

    def _resolve_state(self, text: str, text_lower: str) -> tuple[str, str] | None:
        # Prefer full state names (longest alias first to match "new york" before "york")
        for alias in sorted(STATE_ALIASES, key=len, reverse=True):
            if len(alias) <= 2:
                continue
            if re.search(rf"\b{re.escape(alias)}\b", text_lower):
                abbr = STATE_ALIASES[alias]
                if abbr == "US":
                    return None
                fips = self._states.get(abbr)
                if fips:
                    return abbr, fips
        # Two-letter abbreviations must appear uppercase to avoid matching common words ("in", "or", "me")
        for abbr, fips in self._states.items():
            if len(abbr) == 2 and re.search(rf"\b{re.escape(abbr)}\b", text):
                return abbr, fips
        return None

    def _resolve_county(
        self, text_lower: str, state_abbr: str | None
    ) -> tuple[str, str, str, str] | None:
        best: tuple[str, str, str, str] | None = None
        best_len = 0
        for st, sf, county, cf in self._counties:
            if state_abbr and st != state_abbr:
                continue
            county_lower = county.lower().replace(" county", "")
            if county_lower in text_lower or county.lower() in text_lower:
                if len(county_lower) > best_len:
                    best = (st, sf, county, cf)
                    best_len = len(county_lower)
        return best

    def _state_alias_matched(self, text_lower: str, state_abbr: str) -> bool:
        for alias, abbr in STATE_ALIASES.items():
            if abbr == state_abbr and len(alias) > 2 and re.search(rf"\b{re.escape(alias)}\b", text_lower):
                return True
        return False

    def resolve(self, text: str) -> list[GeoMatch]:
        self._load()
        text_lower = text.lower()
        matches: list[GeoMatch] = []

        state = self._resolve_state(text, text_lower)
        state_abbr = state[0] if state else None
        state_fips = state[1] if state else None

        county_hit: tuple[str, str, str, str] | None = None
        if "county" in text_lower:
            county_hit = self._resolve_county(text_lower, state_abbr)
        elif not state_abbr:
            county_hit = self._resolve_county(text_lower, None)

        if county_hit:
            st, sf, county, cf = county_hit
            # Avoid "New York" → New York County when user meant the state
            county_stem = county.lower().replace(" county", "")
            if state_abbr and self._state_alias_matched(text_lower, state_abbr):
                if county_stem in STATE_ALIASES and STATE_ALIASES[county_stem] == state_abbr:
                    county_hit = None

        if county_hit:
            st, sf, county, cf = county_hit
            matches.append(GeoMatch(state=st, state_fips=sf, county=county, county_fips=cf))
        elif state_abbr and state_fips:
            matches.append(
                GeoMatch(state=state_abbr, state_fips=state_fips, county=None, county_fips=None)
            )

        return matches

    def resolve_states(self, text: str) -> list[GeoMatch]:
        """Resolve ALL distinct states mentioned, in order of appearance.

        Used for multi-state comparison ("compare California and Texas").
        Only state-level matches; ignores ambiguous regions like "the South".
        """
        self._load()
        text_lower = text.lower()
        found: list[tuple[int, GeoMatch]] = []
        seen: set[str] = set()

        for alias in sorted(STATE_ALIASES, key=len, reverse=True):
            if len(alias) <= 2:
                continue
            abbr = STATE_ALIASES[alias]
            if abbr == "US" or abbr in seen:
                continue
            if re.search(rf"\b{re.escape(alias)}\b", text_lower):
                fips = self._states.get(abbr)
                if fips:
                    found.append((text_lower.find(alias), GeoMatch(abbr, fips, None, None)))
                    seen.add(abbr)

        for abbr, fips in self._states.items():
            if len(abbr) == 2 and abbr not in seen and re.search(rf"\b{re.escape(abbr)}\b", text):
                found.append((text.find(abbr), GeoMatch(abbr, fips, None, None)))
                seen.add(abbr)

        found.sort(key=lambda x: x[0])
        return [g for _, g in found]

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
