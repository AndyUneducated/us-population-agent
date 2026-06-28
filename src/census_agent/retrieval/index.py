"""Build and load lexical index over census field descriptions."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from census_agent.config import Settings, get_settings
from census_agent.data.gateway import DataGateway


@dataclass
class IndexedField:
    table_id: str
    table_number: str
    table_title: str
    table_topics: str
    description: str
    physical_table_suffix: str


def _tokenize(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2}


def _lexical_score(query: str, text: str) -> float:
    q_tokens = _tokenize(query)
    if not q_tokens:
        return 0.0
    t_tokens = _tokenize(text)
    return len(q_tokens & t_tokens) / len(q_tokens)


class FieldIndex:
    def __init__(self, entries: list[IndexedField]) -> None:
        self.entries = entries

    def search(self, query: str, top_k: int = 8) -> list[tuple[IndexedField, float]]:
        scores = [
            (_lexical_score(query, f"{e.table_title} {e.description}"), i)
            for i, e in enumerate(self.entries)
        ]
        scores.sort(reverse=True)
        return [(self.entries[i], s) for s, i in scores[:top_k] if s > 0]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(e) for e in self.entries]
        path.write_text(json.dumps(payload), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> FieldIndex:
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries: list[IndexedField] = []
        for item in payload:
            item.pop("embedding", None)
            entries.append(IndexedField(**item))
        return cls(entries)


# Physical tables included in snapshot — only index fields from these groups
INDEX_TABLE_SUFFIXES = ("B01", "B02", "B03", "B15", "B19", "B23", "B25")

TABLE_NUMBER_PREFIXES: dict[str, tuple[str, ...]] = {
    "B01": ("B010",),
    "B02": ("B020",),
    "B03": ("B030",),
    "B15": ("B150",),
    "B19": ("B190",),
    "B23": ("B230",),
    "B25": ("B250",),
}


def _suffix_for_number(table_number: str) -> str:
    for suffix, prefixes in TABLE_NUMBER_PREFIXES.items():
        if any(table_number.startswith(p) for p in prefixes):
            return suffix
    return "B01"


def build_field_index(
    gateway: DataGateway,
    settings: Settings | None = None,
    limit: int | None = 500,
) -> FieldIndex:
    settings = settings or get_settings()
    meta = settings.metadata_table("FIELD_DESCRIPTIONS")

    prefix_filters = " OR ".join(
        f"TABLE_NUMBER LIKE '{p}%'"
        for suffix in INDEX_TABLE_SUFFIXES
        for p in TABLE_NUMBER_PREFIXES[suffix]
    )
    limit_clause = f"LIMIT {limit}" if limit else ""
    sql = f"""
        SELECT TABLE_ID, TABLE_NUMBER, TABLE_TITLE, TABLE_TOPICS,
               CONCAT_WS(' | ', TABLE_TITLE, TABLE_TOPICS,
                 NULLIF(FIELD_LEVEL_3, ''), NULLIF(FIELD_LEVEL_4, ''), NULLIF(FIELD_LEVEL_5, '')
               ) AS DESCRIPTION
        FROM "{meta}"
        WHERE TABLE_ID LIKE '%e%'
          AND ({prefix_filters})
        ORDER BY TABLE_NUMBER, TABLE_ID
        {limit_clause}
    """
    rows = gateway.execute(sql)
    entries: list[IndexedField] = []
    for row in rows:
        desc = str(row["DESCRIPTION"] or row["TABLE_TITLE"])
        suffix = _suffix_for_number(str(row["TABLE_NUMBER"]))
        entries.append(
            IndexedField(
                table_id=str(row["TABLE_ID"]),
                table_number=str(row["TABLE_NUMBER"]),
                table_title=str(row["TABLE_TITLE"]),
                table_topics=str(row["TABLE_TOPICS"] or ""),
                description=desc,
                physical_table_suffix=suffix,
            )
        )
    return FieldIndex(entries)
