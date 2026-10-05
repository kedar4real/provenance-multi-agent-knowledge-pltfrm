from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).parents[2]


class Settings(BaseSettings):
    """Runtime settings from the environment / .env. DSN defaults match docker-compose.yml."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    owner_dsn: str = "postgresql://provenance_owner:owner_dev_pw@127.0.0.1:5432/provenance"
    app_dsn: str = "postgresql://provenance_app:app_dev_pw@127.0.0.1:5432/provenance"
    sql_ro_dsn: str = "postgresql://provenance_sql_ro:sql_ro_dev_pw@127.0.0.1:5432/provenance"
    redis_url: str = "redis://127.0.0.1:6379/0"
    rls_signing_key: SecretStr
    sec_user_agent: str = ""
    principals_path: Path = REPO_ROOT / "config" / "principals.yaml"
    api_keys_path: Path = REPO_ROOT / "config" / "api_keys.local.json"
    routing_path: Path = REPO_ROOT / "config" / "routing.yaml"
    db_pool_max_size: int = 10
    # OpenTelemetry traces go here when set (e.g. http://127.0.0.1:4318 for Jaeger).
    otel_exporter_otlp_endpoint: str | None = None
    load_models: bool = True  # embedder + reranker at API startup; tests turn it off
