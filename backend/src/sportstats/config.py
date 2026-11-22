"""Configuration management using Pydantic Settings."""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    DATABASE_URL: str = "sqlite:///./sportstats.db"

    SECRET_KEY: str = "dev-secret-key-sportstats"
    ADMIN_API_KEY: str = "sportstats-admin-dev-key"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""

    ENABLE_LIVE_FEED: bool = False
    ENABLE_AUTOMATED_COLLECTION: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
