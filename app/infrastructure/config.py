from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # psycopg2 URL — Alembic migration'ları için (sync)
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/ai_decision_engine"

    # LLM Yapılandırması
    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5:7b"
    llm_base_url: str = "http://localhost:11434"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url_async(self) -> str:
        """asyncpg URL — uygulama runtime için (async SQLAlchemy)."""
        return self.database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")


settings = Settings()
