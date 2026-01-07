from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Server Config
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Simulation Config
    default_simulation_duration: int = 60
    max_transactions_per_second: int = 10

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
