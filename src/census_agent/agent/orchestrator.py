"""Agent orchestrator — end-to-end pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import re

from census_agent.agent.executor import QueryExecutor
from census_agent.agent.rewriter import Message, Rewriter
from census_agent.agent.sql_builder import build_metric_sql
from census_agent.agent.sql_generator import generate_sql_llm
from census_agent.agent.synthesizer import synthesize_answer
from census_agent.config import Settings, get_settings
from census_agent.data.gateway import DataGateway, get_data_gateway
from census_agent.guardrails.input import IntentClass, classify_input, refusal_message
from census_agent.guardrails.sql_validator import validate_sql
from census_agent.llm.embeddings import EmbeddingClient
from census_agent.retrieval.index import FieldIndex
from census_agent.retrieval.retriever import SchemaRetriever
from census_agent.semantic.catalog import SemanticCatalog
from census_agent.semantic.geo import GeoResolver
from census_agent.trace import Trace

UNANSWERABLE_PATTERNS = [
    r"\breligio",
    r"\bpolitical party\b",
    r"\bvoting preference\b",
]


@dataclass
class AgentResponse:
    answer: str
    sql: str | None = None
    rows: list[dict[str, Any]] = field(default_factory=list)
    refused: bool = False
    error: str | None = None
    trace: Trace | None = None


class CensusAgent:
    def __init__(
        self,
        gateway: DataGateway | None = None,
        settings: Settings | None = None,
        index: FieldIndex | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._gateway = gateway or get_data_gateway(self._settings)
        self._catalog = SemanticCatalog(self._gateway, self._settings)
        self._geo = GeoResolver(self._gateway, self._settings)
        self._rewriter = Rewriter(self._geo)
        self._executor = QueryExecutor(self._gateway, self._settings)
        self._index = index
        if index is None and self._settings.embedding_index_path.exists():
            self._index = FieldIndex.load(self._settings.embedding_index_path)
        self._retriever = (
            SchemaRetriever(self._catalog, self._index, EmbeddingClient(self._settings))
            if self._index
            else None
        )

    def close(self) -> None:
        self._gateway.close()

    def __enter__(self) -> CensusAgent:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def ask(self, question: str, history: list[Message] | None = None) -> AgentResponse:
        trace = Trace()
        history = history or []

        intent = classify_input(question)
        trace.record("guardrail", intent=intent.value)
        if intent != IntentClass.IN_SCOPE:
            return AgentResponse(
                answer=refusal_message(intent),
                refused=True,
                trace=trace,
            )

        rewritten = self._rewriter.rewrite(question, history)
        trace.record("rewrite", original=question, rewritten=rewritten)

        if any(re.search(p, rewritten, re.IGNORECASE) for p in UNANSWERABLE_PATTERNS):
            return AgentResponse(
                answer=(
                    "That topic isn't available in the US Open Census dataset I have access to. "
                    "I can help with population, age, income, housing, employment, education, "
                    "and related demographics by state or county."
                ),
                error="not_in_dataset",
                trace=trace,
            )

        analysis = self._catalog.analyze_query(rewritten)
        geo = analysis.geo[0] if analysis.geo else self._rewriter.slots.geo

        sql: str | None = None
        if analysis.metric:
            sql = build_metric_sql(analysis.metric, geo, self._settings)
            trace.record("sql_build", mode="metric_fast_path", metric=analysis.metric.id)
        elif self._retriever:
            retrieval = self._retriever.retrieve(rewritten)
            trace.record("retrieval", source=retrieval.source, fields=len(retrieval.fields))
            if not retrieval.fields:
                return AgentResponse(
                    answer=(
                        "I couldn't identify census fields to answer that question. "
                        "Try asking about population, median income, unemployment, or housing."
                    ),
                    error="retrieval_miss",
                    trace=trace,
                )
            try:
                sql = generate_sql_llm(rewritten, retrieval.fields, self._settings)
                trace.record("sql_build", mode="llm")
            except Exception as e:
                return AgentResponse(
                    answer=f"I had trouble generating a query: {e}",
                    error="sql_generation_failed",
                    trace=trace,
                )
        else:
            return AgentResponse(
                answer=(
                    "I need a metric hint or an embedding index to answer that question. "
                    "Try: 'What is the population of California?'"
                ),
                error="no_path",
                trace=trace,
            )

        validation = validate_sql(sql, self._settings)
        trace.record("sql_validate", ok=validation.ok, error=validation.error)
        if not validation.ok:
            return AgentResponse(
                answer=f"I generated a query that failed validation: {validation.error}",
                sql=sql,
                error="sql_invalid",
                trace=trace,
            )

        try:
            rows = self._executor.run(validation.sql)
            trace.record("execute", row_count=len(rows))
        except Exception as e:
            return AgentResponse(
                answer=(
                    "I'm having trouble running the census query right now. "
                    f"Details: {e}"
                ),
                sql=validation.sql,
                error="execution_failed",
                trace=trace,
            )

        answer = synthesize_answer(question, validation.sql, rows, self._settings)
        trace.record("synthesize", done=True)
        return AgentResponse(
            answer=answer,
            sql=validation.sql,
            rows=rows,
            trace=trace,
        )
