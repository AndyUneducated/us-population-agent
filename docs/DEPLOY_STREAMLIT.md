# Streamlit Community Cloud Deployment

## Pre-flight checklist

1. Code pushed to GitHub
2. Snowflake **Network Policy** allows Streamlit Cloud egress IPs (see below)
3. Snowflake **PAT** (Personal Access Token) used as `SNOWFLAKE_PASSWORD` (browser SSO does not work on Cloud)
4. Gemini API key ready

## Create the app

| Field | Value |
| --- | --- |
| Repository | Your GitHub repo |
| Branch | `main` |
| Main file path | `app.py` |
| Python version | **3.12** (3.11+ also works) |

## Secrets (Advanced settings → Secrets)

Paste this **TOML** and replace the two secret placeholders:

```toml
DATA_BACKEND = "snowflake"
CENSUS_YEAR = "2020"

SNOWFLAKE_ACCOUNT = "EXLVOFZ-BDC49406"
SNOWFLAKE_USER = "ANDYWALKMAN"
SNOWFLAKE_PASSWORD = "your Snowflake PAT"
SNOWFLAKE_ROLE = "ACCOUNTADMIN"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "US_OPEN_CENSUS_DATA__NEIGHBORHOOD_INSIGHTS__FREE_DATASET"
SNOWFLAKE_SCHEMA = "PUBLIC"

LLM_PROVIDER = "gemini"
GEMINI_API_KEY = "your Gemini API key"
GEMINI_MODEL = "gemini-flash-lite-latest"
```

Click **Save**, wait ~1 minute, then **Reboot** the app.

### Field reference

| Secret | Description |
| --- | --- |
| `DATA_BACKEND` | Must be `snowflake` on Cloud (no DuckDB snapshot in the repo) |
| `CENSUS_YEAR` | `2020` = latest ACS vintage in this dataset; `2019` also available |
| `SNOWFLAKE_ACCOUNT` | Snowflake UI → Profile → Account identifier |
| `SNOWFLAKE_PASSWORD` | PAT token (preferred over login password) |
| `GEMINI_API_KEY` | From [Google AI Studio](https://aistudio.google.com/apikey) |
| `GEMINI_MODEL` | Free tier: `gemini-flash-lite-latest` |

Local template: [`.streamlit/secrets.toml.example`](../.streamlit/secrets.toml.example)

## Snowflake network policy

Streamlit Cloud connects to Snowflake over the public internet. If the app fails to connect, add a **Network Rule** or relax the Network Policy for Cloud egress IPs. Local works but Cloud does not → almost always this issue.

## Local secrets debugging (optional)

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with real values (gitignored)
streamlit run app.py
```

## Cloud capabilities

- **Metric fast path** (population, income, unemployment, etc.): works without a local field index; queries Snowflake directly.
- **LLM SQL path** (complex field questions): needs `field_embeddings.json`, which is not in the repo by default. Metric questions and graceful degradation still work.

## Smoke test after deploy

1. `What is the total population of California?`
2. `What about Texas?` (multi-turn)
3. `What is the weather today?` (should refuse politely)

Sidebar should show `Backend: snowflake`, `LLM: gemini`, and data vintage **2020**.
