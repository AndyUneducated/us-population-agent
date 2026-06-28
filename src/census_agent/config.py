"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


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
    census_year: int = field(default_factory=lambda: int(_env("CENSUS_YEAR", "2019")))

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

    # LLM / embeddings (Ollama default)
    llm_provider: str = field(default_factory=lambda: _env("LLM_PROVIDER", "ollama").lower())
    ollama_base_url: str = field(
        default_factory=lambda: _env("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    )
    ollama_embed_model: str = field(
        default_factory=lambda: _env("OLLAMA_EMBED_MODEL", "qwen3-embedding:8b")
    )
    ollama_model_fast: str = field(
        default_factory=lambda: _env("OLLAMA_MODEL_FAST", "qwen3.5:9b")
    )
    ollama_model_main: str = field(
        default_factory=lambda: _env("OLLAMA_MODEL_MAIN", "qwen3.5:9b")
    )
    query_timeout_seconds: int = field(
        default_factory=lambda: int(_env("QUERY_TIMEOUT_SECONDS", "30"))
    )
    sql_row_limit: int = field(default_factory=lambda: int(_env("SQL_ROW_LIMIT", "100")))

    @property
    def snowflake_fqn(self) -> str:
        return f'"{self.snowflake_database}"."{self.snowflake_schema}"'

    def table_name(self, suffix: str) -> str:
        """Physical table name for a census year, e.g. 2019_CBG_B01."""
        return f"{self.census_year}_CBG_{suffix}"

    def metadata_table(self, name: str) -> str:
        return f"{self.census_year}_METADATA_CBG_{name}"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
