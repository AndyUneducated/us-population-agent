"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field, replace
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[2]


def _load_streamlit_secrets() -> None:
    """Merge Streamlit secrets into os.environ (Community Cloud + local secrets.toml)."""
    try:
        import streamlit as st
    except ImportError:
        return
    try:
        items = list(st.secrets.items())
    except Exception:
        return
    for key, value in items:
        if isinstance(value, dict):
            section = str(key).upper()
            for subkey, subval in value.items():
                env_key = f"{section}_{str(subkey).upper()}"
                os.environ.setdefault(env_key, str(subval))
        else:
            os.environ.setdefault(str(key), str(value))


def _bootstrap_env() -> None:
    load_dotenv(_ROOT / ".env")
    _load_streamlit_secrets()


_bootstrap_env()


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _available_duckdb_years(path: Path) -> list[int]:
    """Return census vintages present in a local DuckDB snapshot (newest first)."""
    import duckdb

    conn = duckdb.connect(str(path), read_only=True)
    try:
        rows = conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchall()
        years: set[int] = set()
        for (name,) in rows:
            match = re.match(r"^(\d{4})_", str(name))
            if match:
                years.add(int(match.group(1)))
        return sorted(years, reverse=True)
    finally:
        conn.close()


def resolve_census_year(settings: Settings) -> int:
    """Use configured year, or the newest vintage available in DuckDB."""
    configured = settings.census_year
    if settings.data_backend != "duckdb" or not settings.duckdb_path.exists():
        return configured
    available = _available_duckdb_years(settings.duckdb_path)
    if not available:
        return configured
    if configured in available:
        return configured
    return available[0]


@dataclass(frozen=True)
class Settings:
    """Runtime settings for data access, LLM, and paths."""

    # Snowflake
    snowflake_account: str = field(default_factory=lambda: _env("SNOWFLAKE_ACCOUNT"))
    snowflake_user: str = field(default_factory=lambda: _env("SNOWFLAKE_USER"))
    snowflake_password: str = field(default_factory=lambda: _env("SNOWFLAKE_PASSWORD"))
    snowflake_role: str = field(default_factory=lambda: _env("SNOWFLAKE_ROLE", "ACCOUNTADMIN"))
    snowflake_warehouse: str = field(
        default_factory=lambda: _env("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
    )
    snowflake_database: str = field(default_factory=lambda: _env("SNOWFLAKE_DATABASE"))
    snowflake_schema: str = field(default_factory=lambda: _env("SNOWFLAKE_SCHEMA", "PUBLIC"))
    snowflake_authenticator: str = field(default_factory=lambda: _env("SNOWFLAKE_AUTHENTICATOR"))

    # Data backend: snowflake | duckdb
    data_backend: str = field(default_factory=lambda: _env("DATA_BACKEND", "duckdb").lower())

    # Census vintage
    census_year: int = field(default_factory=lambda: int(_env("CENSUS_YEAR", "2020")))

    # Local artifacts
    project_root: Path = field(default_factory=lambda: _ROOT)
    data_dir: Path = field(default_factory=lambda: _ROOT / "data")
    duckdb_path: Path = field(
        default_factory=lambda: Path(_env("DUCKDB_PATH", str(_ROOT / "data" / "census.duckdb")))
    )
    embedding_index_path: Path = field(
        default_factory=lambda: Path(
            _env("EMBEDDING_INDEX_PATH", str(_ROOT / "data" / "field_embeddings.json"))
        )
    )

    # LLM (Google Gemini)
    llm_provider: str = field(default_factory=lambda: _env("LLM_PROVIDER", "gemini").lower())
    gemini_api_key: str = field(default_factory=lambda: _env("GEMINI_API_KEY"))
    gemini_model: str = field(
        default_factory=lambda: _env("GEMINI_MODEL", "gemini-flash-lite-latest")
    )
    gemini_base_url: str = field(
        default_factory=lambda: _env(
            "GEMINI_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta",
        )
    )
    query_timeout_seconds: int = field(
        default_factory=lambda: int(_env("QUERY_TIMEOUT_SECONDS", "30"))
    )
    sql_row_limit: int = field(default_factory=lambda: int(_env("SQL_ROW_LIMIT", "100")))

    @property
    def snowflake_fqn(self) -> str:
        return f'"{self.snowflake_database}"."{self.snowflake_schema}"'

    def table_name(self, suffix: str) -> str:
        """Physical table name for a census year, e.g. 2020_CBG_B01."""
        return f"{self.census_year}_CBG_{suffix}"

    def metadata_table(self, name: str) -> str:
        return f"{self.census_year}_METADATA_CBG_{name}"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        base = Settings()
        resolved = resolve_census_year(base)
        _settings = replace(base, census_year=resolved) if resolved != base.census_year else base
    return _settings
