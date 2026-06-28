"""Agent orchestrator — end-to-end pipeline."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from census_agent.agent.degradation import (
    DegradationKind,
    degradation_for,
    detect_ambiguous_geo,
    detect_prompt_injection,
    detect_zip_question,
)
from census_agent.agent.executor import QueryExecutor
from census_agent.agent.rewriter import Message, Rewriter
from census_agent.agent.sql_builder import build_comparison_sql, build_metric_sql
from census_agent.agent.sql_generator import generate_sql_llm
from census_agent.agent.synthesizer import synthesize_answer
from census_agent.config import Settings, get_settings
from census_agent.data.gateway import DataGateway, get_data_gateway
from census_agent.guardrails.faithfulness import check_faithfulness
from census_agent.guardrails.input import IntentClass, classify_input, refusal_message
from census_agent.guardrails.sql_validator import validate_sql
from census_agent.observability.trace_store import append_trace
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
    failure_mode: str | None = None
    faithful: bool | None = None
    trace: Trace | None = None


class CensusAgent:
    def __init__(
        self,
        gateway: DataGateway | None = None,
        settings: Settings | None = None,
        index: FieldIndex | None = None,
        *,
        persist_traces: bool = True,
    ) -> None:
        self._settings = settings or get_settings()
        self._gateway = gateway or get_data_gateway(self._settings)
        self._catalog = SemanticCatalog(self._gateway, self._settings)
        self._geo = GeoResolver(self._gateway, self._settings)
        self._rewriter = Rewriter(self._geo)
        self._executor = QueryExecutor(self._gateway, self._settings)
        self._persist_traces = persist_traces
        self._index = index
        if index is None and self._settings.embedding_index_path.exists():
            self._index = FieldIndex.load(self._settings.embedding_index_path)
        self._retriever = (
            SchemaRetriever(self._catalog, self._index, self._settings) if self._index else None
        )

    def close(self) -> None:
        self._gateway.close()

    def __enter__(self) -> CensusAgent:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _respond(
        self,
        *,
        question: str,
        trace: Trace,
        answer: str,
        sql: str | None = None,
        rows: list[dict[str, Any]] | None = None,
        refused: bool = False,
        error: str | None = None,
        failure_mode: str | None = None,
        faithful: bool | None = None,
    ) -> AgentResponse:
        resp = AgentResponse(
            answer=answer,
            sql=sql,
            rows=rows or [],
            refused=refused,
            error=error,
            failure_mode=failure_mode,
            faithful=faithful,
            trace=trace,
        )
        if self._persist_traces:
            append_trace(
                question=question,
                trace=trace,
                answer=answer,
                sql=sql,
                error=error,
                refused=refused,
                settings=self._settings,
            )
        return resp

    def _generate_sql_with_retry(
        self,
        question: str,
        fields: list,
        trace: Trace,
    ) -> tuple[str | None, str | None]:
        try:
            sql = generate_sql_llm(question, fields, self._settings)
            trace.record("sql_build", mode="llm", attempt=1)
        except Exception as e:
            return None, f"sql_generation_failed:{e}"

        validation = validate_sql(sql, self._settings)
        if validation.ok:
            return validation.sql, None

        trace.record("sql_validate", ok=False, error=validation.error, attempt=1)
        repair_prompt = (
            f"{question}\n\n"
            f"The previous SQL failed validation: {validation.error}\n"
            f"Previous SQL:\n{sql}\n"
            "Fix the SQL and return only one valid SELECT."
        )
        try:
            sql = generate_sql_llm(repair_prompt, fields, self._settings)
            trace.record("sql_build", mode="llm_repair", attempt=2)
        except Exception as e:
            return sql, f"sql_generation_failed:{e}"

        validation = validate_sql(sql, self._settings)
        trace.record("sql_validate", ok=validation.ok, error=validation.error, attempt=2)
        if not validation.ok:
            return sql, f"sql_invalid:{validation.error}"
        return validation.sql, None

    def ask(self, question: str, history: list[Message] | None = None) -> AgentResponse:
        trace = Trace()
        history = history or []

        intent = classify_input(question)
        trace.record("guardrail", intent=intent.value)
        if detect_prompt_injection(question):
            deg = degradation_for(DegradationKind.PROMPT_INJECTION)
            trace.record("degradation", kind=deg.kind.value)
            return self._respond(
                question=question,
                trace=trace,
                answer=deg.user_message,
                error=deg.error_code,
                failure_mode="prompt_injection",
            )

        if intent != IntentClass.IN_SCOPE:
            return self._respond(
                question=question,
                trace=trace,
                answer=refusal_message(intent),
                refused=True,
                failure_mode="refusal_correct" if intent == IntentClass.OUT_OF_SCOPE else "unsafe_blocked",
            )

        rewritten = self._rewriter.rewrite(question, history)
        trace.record("rewrite", original=question, rewritten=rewritten)

        if detect_zip_question(rewritten):
            deg = degradation_for(DegradationKind.ZIP_GRANULARITY)
            trace.record("degradation", kind=deg.kind.value)
            return self._respond(
                question=question,
                trace=trace,
                answer=deg.user_message,
                error=deg.error_code,
                failure_mode="zip_granularity",
            )

        if any(re.search(p, rewritten, re.IGNORECASE) for p in UNANSWERABLE_PATTERNS):
            return self._respond(
                question=question,
                trace=trace,
                answer=(
                    "That topic isn't available in the US Open Census dataset I have access to. "
                    "I can help with population, age, income, housing, employment, education, "
                    "and related demographics by state or county."
                ),
                error="not_in_dataset",
                failure_mode="not_in_dataset",
            )

        ambiguous_geo = detect_ambiguous_geo(rewritten)
        analysis = self._catalog.analyze_query(rewritten)
        geo = analysis.geo[0] if analysis.geo else self._rewriter.slots.geo
        trace.record(
            "plan",
            metric=analysis.metric.id if analysis.metric else None,
            geo=geo.label if geo else None,
            ambiguous_geo=ambiguous_geo,
        )

        sql: str | None = None
        if analysis.metric:
            # Detect multi-state comparisons from the original question: the
            # rewriter collapses multi-geo queries to a single standalone geo.
            compare_geos = self._catalog.geo_resolver.resolve_states(question)
            if len(compare_geos) >= 2:
                sql = build_comparison_sql(analysis.metric, compare_geos, self._settings)
                trace.record(
                    "sql_build",
                    mode="metric_comparison",
                    metric=analysis.metric.id,
                    states=[g.state for g in compare_geos],
                )
            else:
                sql = build_metric_sql(analysis.metric, geo, self._settings)
                trace.record("sql_build", mode="metric_fast_path", metric=analysis.metric.id)
        elif self._retriever:
            retrieval = self._retriever.retrieve(rewritten)
            trace.record("retrieval", source=retrieval.source, fields=len(retrieval.fields))
            if not retrieval.fields:
                return self._respond(
                    question=question,
                    trace=trace,
                    answer=(
                        "I couldn't identify census fields to answer that question. "
                        "Try asking about population, median income, unemployment, or housing."
                    ),
                    error="retrieval_miss",
                    failure_mode="retrieval_miss",
                )
            sql, gen_error = self._generate_sql_with_retry(rewritten, retrieval.fields, trace)
            if gen_error:
                if gen_error.startswith("sql_invalid"):
                    return self._respond(
                        question=question,
                        trace=trace,
                        answer="I generated a query that failed validation after a repair attempt.",
                        sql=sql,
                        error="sql_invalid",
                        failure_mode="sql_generation_error",
                    )
                return self._respond(
                    question=question,
                    trace=trace,
                    answer="I had trouble generating a census query for that question.",
                    error="sql_generation_failed",
                    failure_mode="sql_generation_error",
                )
        else:
            return self._respond(
                question=question,
                trace=trace,
                answer=(
                    "I need a metric hint or an embedding index to answer that question. "
                    "Try: 'What is the population of California?'"
                ),
                error="no_path",
                failure_mode="no_path",
            )

        validation = validate_sql(sql, self._settings)
        trace.record("sql_validate", ok=validation.ok, error=validation.error)
        if not validation.ok:
            return self._respond(
                question=question,
                trace=trace,
                answer="I generated a query that failed validation.",
                sql=sql,
                error="sql_invalid",
                failure_mode="sql_generation_error",
            )

        try:
            rows = self._executor.run(validation.sql)
            trace.record("execute", row_count=len(rows))
        except Exception as e:
            trace.record("execute_error", error=str(e))
            deg = degradation_for(DegradationKind.EXECUTION_FAILED)
            return self._respond(
                question=question,
                trace=trace,
                answer=deg.user_message,
                sql=validation.sql,
                error=deg.error_code,
                failure_mode="execution_failed",
            )

        if not rows:
            deg = degradation_for(DegradationKind.EMPTY_RESULT)
            trace.record("degradation", kind=deg.kind.value)
            return self._respond(
                question=question,
                trace=trace,
                answer=deg.user_message,
                sql=validation.sql,
                rows=[],
                error=deg.error_code,
                failure_mode="empty_result",
            )

        answer = synthesize_answer(question, validation.sql, rows, self._settings)
        if ambiguous_geo and not geo:
            note = degradation_for(
                DegradationKind.AMBIGUOUS_GEO,
                year=str(self._settings.census_year),
                region="the South / Midwest / Northeast",
            )
            answer = f"{note.user_message}\n\n{answer}"
        elif ambiguous_geo:
            note = degradation_for(
                DegradationKind.AMBIGUOUS_GEO,
                year=str(self._settings.census_year),
                region=geo.label if geo else "the region",
            )
            answer = f"*{note.user_message}*\n\n{answer}"

        faithful, faith_reason = check_faithfulness(answer, rows)
        trace.record("faithfulness", ok=faithful, reason=faith_reason)
        trace.record("synthesize", done=True)
        return self._respond(
            question=question,
            trace=trace,
            answer=answer,
            sql=validation.sql,
            rows=rows,
            faithful=faithful,
            failure_mode=None if faithful else "hallucination_risk",
        )
