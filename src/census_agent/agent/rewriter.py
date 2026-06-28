"""Conversation slots and context rewriting."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from census_agent.semantic.geo import GeoMatch, GeoResolver
from census_agent.semantic.metrics import MetricDefinition, match_metric


@dataclass
class ConversationSlots:
    metric: MetricDefinition | None = None
    geo: GeoMatch | None = None
    year: int | None = None


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
        metric = match_metric(query)
        geo_matches = self.geo_resolver.resolve(query)

        if metric:
            self.slots.metric = metric
        elif history:
            for msg in reversed(history):
                if msg.role == "user":
                    m = match_metric(msg.content)
                    if m:
                        self.slots.metric = m
                        break

        if geo_matches:
            self.slots.geo = geo_matches[0]
        elif self._is_followup(query) and self.slots.geo:
            pass  # keep prior geo
        elif history and self._is_followup(query):
            for msg in reversed(history):
                if msg.role == "user":
                    gm = self.geo_resolver.resolve(msg.content)
                    if gm:
                        self.slots.geo = gm[0]
                        break

        return self._standalone_question(query)

    def _is_followup(self, query: str) -> bool:
        q = query.lower()
        return bool(
            re.search(r"\b(what about|how about|and|same for|there)\b", q)
            or re.match(r"^(what|how) about\b", q)
        )

    def _standalone_question(self, query: str) -> str:
        if not self._is_followup(query) and match_metric(query):
            return query

        parts: list[str] = []
        if self.slots.metric:
            parts.append(self.slots.metric.name.lower())
        else:
            parts.append(query.rstrip("?").strip())

        if self.slots.geo:
            parts.append(f"in {self.slots.geo.label}")

        if self._is_followup(query):
            return " ".join(parts) + "?"
        return query
