"""Schema retriever: fast-path metrics + vector search over field index."""

from __future__ import annotations

from dataclasses import dataclass

from census_agent.config import Settings, get_settings
from census_agent.llm.embeddings import EmbeddingClient
from census_agent.retrieval.index import FieldIndex
from census_agent.semantic.catalog import FieldInfo, SemanticCatalog


@dataclass
class RetrievalResult:
    source: str
    fields: list[FieldInfo]
    scores: list[float]


class SchemaRetriever:
    def __init__(
        self,
        catalog: SemanticCatalog,
        index: FieldIndex,
        embedder: EmbeddingClient | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._catalog = catalog
        self._index = index
        self._embedder = embedder or EmbeddingClient(settings)
        self._settings = settings or get_settings()

    def retrieve(self, query: str, top_k: int = 8) -> RetrievalResult:
        analysis = self._catalog.analyze_query(query)
        if analysis.metric and analysis.fields:
            return RetrievalResult(
                source="metric_fast_path",
                fields=analysis.fields,
                scores=[1.0],
            )

        q_emb = self._embedder.embed(query)
        hits = self._index.search(q_emb, top_k=top_k)
        fields = [
            FieldInfo(
                table_id=h.table_id,
                table_number=h.table_number,
                table_title=h.table_title,
                table_topics=h.table_topics,
                description=h.description,
                physical_table=self._catalog.physical_table(h.physical_table_suffix),
                column_name=h.table_id,
            )
            for h, _ in hits
        ]
        scores = [s for _, s in hits]
        return RetrievalResult(source="vector_retrieval", fields=fields, scores=scores)
