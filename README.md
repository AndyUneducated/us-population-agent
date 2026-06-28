# US Population Chat Agent

Snowflake Applied AI homework: a census-grounded chat agent over US Open Census data (ACS at census block group granularity).

**Default data vintage:** `2020` ACS 5-year estimates (latest available in the Marketplace dataset; `2019` also supported).

## Features

- **Data Gateway** — read-only SQL over Snowflake (deploy) or local DuckDB snapshot (dev)
- **Semantic Catalog** — curated metrics, FIPS geo resolution, field metadata
- **Agent pipeline** — guardrails, multi-turn rewriter, text-to-SQL, faithfulness checks
- **Streamlit UI** — chat, SQL expander, thumbs up/down feedback
- **Eval harness** — golden dataset + regression gate (`evals/golden.jsonl`)

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # fill SNOWFLAKE_PASSWORD and GEMINI_API_KEY
```

### Local DuckDB snapshot (optional, for offline dev)

```bash
python scripts/etl_snapshot.py
python scripts/build_embeddings.py 200
```

Set `DATA_BACKEND=duckdb` in `.env` to use the snapshot.

### Verify

```bash
pytest -m "not e2e"
python scripts/verify_phase1.py
python scripts/verify_phase2.py
python scripts/verify_phase3.py
python scripts/verify_phase4.py
python scripts/verify_phase5.py
python scripts/test_gemini.py
```

### Run chat UI

```bash
streamlit run app.py
```

## Deploy (Streamlit Community Cloud)

Production uses **live Snowflake** (`DATA_BACKEND=snowflake`) and **Google Gemini** for LLM SQL generation.

See **[`docs/DEPLOY_STREAMLIT.md`](docs/DEPLOY_STREAMLIT.md)** for the exact Secrets TOML to paste in the Streamlit UI.

- Main file: `app.py`
- Dependencies: `requirements.txt`
- Set `CENSUS_YEAR = "2020"` in Secrets

## Documentation

- [`docs/ASSIGNMENT.md`](docs/ASSIGNMENT.md) — homework requirements
- [`docs/TECHNICAL_DESIGN.md`](docs/TECHNICAL_DESIGN.md) — architecture and phases
- [`docs/DEPLOY_STREAMLIT.md`](docs/DEPLOY_STREAMLIT.md) — cloud deployment
