#!/usr/bin/env python3
"""Phase 1 acceptance checks: metrics, geo, retrieval."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from census_agent.config import get_settings
from census_agent.data.gateway import get_data_gateway
from census_agent.llm.embeddings import EmbeddingClient
from census_agent.retrieval.index import FieldIndex
from census_agent.retrieval.retriever import SchemaRetriever
from census_agent.semantic.catalog import SemanticCatalog
from census_agent.semantic.metrics import match_metric


def main() -> int:
    settings = get_settings()
    errors: list[str] = []

    # Metric fast path
    cases = [
        ("What is the total population of California?", "B01003e1"),
        ("median household income in Texas", "B19013e1"),
        ("median age", "B01002e1"),
    ]
    for q, expected_col in cases:
        m = match_metric(q)
        if not m or m.column != expected_col:
            errors.append(f"metric fail: {q!r} -> {m}")
        else:
            print(f"OK metric: {q!r} -> {m.column}")

    with get_data_gateway() as gw:
        catalog = SemanticCatalog(gw)

        # Geo resolution
        geo_cases = [
            ("California population", "CA", None),
            ("Santa Clara County median income", "CA", "Santa Clara"),
        ]
        for q, exp_state, exp_county_fragment in geo_cases:
            matches = catalog.geo_resolver.resolve(q)
            if not matches:
                errors.append(f"geo fail: no match for {q!r}")
                continue
            g = matches[0]
            if g.state != exp_state:
                errors.append(f"geo state fail: {q!r} -> {g.state}")
            elif exp_county_fragment and (not g.county or exp_county_fragment not in g.county):
                errors.append(f"geo county fail: {q!r} -> {g.county}")
            else:
                print(f"OK geo: {q!r} -> {g.label}")

        # Vector retrieval (if index exists)
        if settings.embedding_index_path.exists():
            index = FieldIndex.load(settings.embedding_index_path)
            retriever = SchemaRetriever(catalog, index, EmbeddingClient(settings))
            r = retriever.retrieve("unemployment rate by county")
            if not r.fields:
                errors.append("retrieval fail: no fields for unemployment")
            else:
                print(f"OK retrieval: unemployment -> {r.fields[0].column_name} ({r.source})")
        else:
            print("SKIP retrieval: run scripts/build_embeddings.py first")

    if errors:
        print("\nFAILED:")
        for e in errors:
            print(" -", e)
        return 1
    print("\nPhase 1 acceptance: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
