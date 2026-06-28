# US Population Chat Agent

Snowflake Applied AI homework: a census-grounded chat agent over US Open Census data.

## Phase 1 (current)

Data layer and semantic catalog:

- **Data Gateway** — read-only SQL over Snowflake or local DuckDB snapshot
- **Semantic Catalog** — curated metrics, geo (FIPS) resolution, field metadata
- **Schema Retriever** — metric fast-path + Ollama embedding search over field descriptions

### Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # fill SNOWFLAKE_PASSWORD
```

### Build local snapshot (from Snowflake)

```bash
python scripts/etl_snapshot.py
```

### Build embedding index (requires Ollama)

```bash
ollama serve
python scripts/build_embeddings.py 200
```

### Verify

```bash
pytest
python scripts/verify_phase1.py
python scripts/verify_phase2.py
python scripts/verify_phase3.py
```

### Run chat UI

```bash
streamlit run app.py
```

See [`docs/TECHNICAL_DESIGN.md`](docs/TECHNICAL_DESIGN.md) for full architecture.
