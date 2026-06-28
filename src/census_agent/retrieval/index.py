"""Build and load vector index over census field descriptions."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from census_agent.config import Settings, get_settings
from census_agent.data.gateway import DataGateway
from census_agent.llm.embeddings import EmbeddingClient


@dataclass
class IndexedField:
    table_id: str
    table_number: str
    table_title: str
    table_topics: str
    description: str
    physical_table_suffix: str
    embedding: list[float]


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


class FieldIndex:
    def __init__(self, entries: list[IndexedField]) -> None:
        self.entries = entries
        self._matrix = np.array([e.embedding for e in entries], dtype=np.float32)

    def search(self, query_embedding: list[float], top_k: int = 8) -> list[tuple[IndexedField, float]]:
        q = np.array(query_embedding, dtype=np.float32)
        scores = [(_cosine(q, self._matrix[i]), i) for i in range(len(self.entries))]
        scores.sort(reverse=True)
        return [(self.entries[i], s) for s, i in scores[:top_k]]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(e) for e in self.entries]
        path.write_text(json.dumps(payload), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> FieldIndex:
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = [IndexedField(**item) for item in payload]
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
    embedder: EmbeddingClient,
    settings: Settings | None = None,
    limit: int | None = 500,
) -> FieldIndex:
    settings = settings or get_settings()
    meta = settings.metadata_table("FIELD_DESCRIPTIONS")

    # Only estimate columns (e*) to reduce noise
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
    for i, row in enumerate(rows):
        desc = str(row["DESCRIPTION"] or row["TABLE_TITLE"])
        text = f"{row['TABLE_TITLE']}: {desc}"
        vec = embedder.embed(text)
        suffix = _suffix_for_number(str(row["TABLE_NUMBER"]))
        entries.append(
            IndexedField(
                table_id=str(row["TABLE_ID"]),
                table_number=str(row["TABLE_NUMBER"]),
                table_title=str(row["TABLE_TITLE"]),
                table_topics=str(row["TABLE_TOPICS"] or ""),
                description=desc,
                physical_table_suffix=suffix,
                embedding=vec,
            )
        )
    return FieldIndex(entries)
