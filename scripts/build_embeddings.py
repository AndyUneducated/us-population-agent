#!/usr/bin/env python3
"""Build embedding index over census field descriptions."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from census_agent.config import get_settings
from census_agent.data.gateway import get_data_gateway
from census_agent.llm.embeddings import EmbeddingClient
from census_agent.logging_setup import setup_logging
from census_agent.retrieval.index import build_field_index

logger = setup_logging()


def main() -> int:
    settings = get_settings()
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    logger.info("Building field index (limit=%d) ...", limit)

    with get_data_gateway() as gw:
        embedder = EmbeddingClient(settings)
        index = build_field_index(gw, embedder, settings, limit=limit)

    settings.embedding_index_path.parent.mkdir(parents=True, exist_ok=True)
    index.save(settings.embedding_index_path)
    logger.info("Saved %d entries to %s", len(index.entries), settings.embedding_index_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
