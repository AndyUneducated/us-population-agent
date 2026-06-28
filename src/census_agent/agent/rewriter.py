"""Conversation slots and context rewriting."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from census_agent.semantic.geo import GeoMatch, GeoResolver
from census_agent.semantic.metrics import MetricDefinition, match_metric

# Scan at most this many prior messages when rebuilding slots (~6 turns).
_MAX_HISTORY_MESSAGES = 12

_FOLLOWUP_RE = re.compile(
    r"\b(what about|how about|and|same for|there)\b|^(what|how) about\b",
    re.IGNORECASE,
)
_WHAT_ABOUT_RE = re.compile(r"^(?:what|how) about\s+(.+?)\??$", re.IGNORECASE)
_SAME_FOR_RE = re.compile(r"^same for\s+(.+?)\??$", re.IGNORECASE)
_AND_PLACE_RE = re.compile(r"^and\s+(.+?)\??$", re.IGNORECASE)


@dataclass
class ConversationSlots:
    metric: MetricDefinition | None = None
    geo: GeoMatch | None = None
    year: int | None = None
    # Active multi-region comparison set (>=2 states). Empty for single-region turns.
    compare_geos: list[GeoMatch] = field(default_factory=list)


@dataclass
class Message:
    role: str
    content: str


@dataclass
class Rewriter:
    geo_resolver: GeoResolver
    slots: ConversationSlots = field(default_factory=ConversationSlots)

    def rewrite(self, query: str, history: list[Message] | None = None) -> str:
        history = history or []
        if len(history) > _MAX_HISTORY_MESSAGES:
            history = history[-_MAX_HISTORY_MESSAGES:]
        slots = self._slots_from_history(history)
        slots = self._apply_query(query, slots)
        self.slots = slots
        return self._standalone_question(query, slots)

    def _slots_from_history(self, history: list[Message]) -> ConversationSlots:
        """Rebuild slots from recent history.

        User messages take priority (the human's intent), with assistant messages
        as a fallback for seeded conversations. This prevents refusal/degradation
        replies (which list capability keywords like "population, income, ...")
        from polluting the inherited metric/geo.
        """
        users = [m.content for m in history if m.role == "user"]
        assistants = [m.content for m in history if m.role == "assistant"]
        slots = ConversationSlots()
        slots.metric = self._last_metric(users) or self._last_metric(assistants)
        slots.geo = self._last_geo(users) or self._last_geo(assistants)
        slots.compare_geos = self._last_compare(users)
        return slots

    def _last_metric(self, contents: list[str]) -> MetricDefinition | None:
        for content in reversed(contents):
            metric = match_metric(content)
            if metric:
                return metric
        return None

    def _last_geo(self, contents: list[str]) -> GeoMatch | None:
        for content in reversed(contents):
            geo_matches = self.geo_resolver.resolve(content)
            if geo_matches:
                return geo_matches[0]
        return None

    def _last_compare(self, contents: list[str]) -> list[GeoMatch]:
        """Most recent user turn that named >=2 states defines the comparison set."""
        for content in reversed(contents):
            states = self.geo_resolver.resolve_states(content)
            if len(states) >= 2:
                return states
        return []

    def _apply_query(self, query: str, slots: ConversationSlots) -> ConversationSlots:
        metric = match_metric(query)
        if metric:
            slots.metric = metric

        current_states = self.geo_resolver.resolve_states(query)
        geo_matches = self.geo_resolver.resolve(query)

        if len(current_states) >= 2:
            # This turn names a fresh comparison set (e.g. "compare CA and TX",
            # "what about FL and WA?"). It overrides any prior comparison.
            slots.compare_geos = current_states
            slots.geo = current_states[0]
        elif geo_matches:
            # A single concrete geo this turn collapses back to single-region mode.
            slots.geo = geo_matches[0]
            slots.compare_geos = []
        elif self._is_followup(query):
            # Metric-only follow-up ("what about income?"): keep the inherited
            # comparison set (if any) and geo so context survives.
            if extracted := self._extract_followup_geo(query):
                slots.geo = extracted
                slots.compare_geos = []
        return slots

    def _extract_followup_geo(self, query: str) -> GeoMatch | None:
        for pattern in (_WHAT_ABOUT_RE, _SAME_FOR_RE, _AND_PLACE_RE):
            match = pattern.match(query.strip())
            if match:
                geo_matches = self.geo_resolver.resolve(match.group(1).strip())
                if geo_matches:
                    return geo_matches[0]
        return None

    def _is_followup(self, query: str) -> bool:
        return bool(_FOLLOWUP_RE.search(query.strip()))

    def _standalone_question(self, query: str, slots: ConversationSlots) -> str:
        if not self._is_followup(query) and match_metric(query):
            return query

        if not self._is_followup(query):
            return query

        parts: list[str] = []
        if slots.metric:
            parts.append(slots.metric.name.lower())
        else:
            parts.append(query.rstrip("?").strip())

        if slots.geo:
            parts.append(f"in {slots.geo.label}")

        return " ".join(parts) + "?"
