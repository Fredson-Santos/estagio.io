from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "estagio.io API"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str
    CORS_ORIGINS: list[str] = [
        "http://localhost:4321",
        "http://127.0.0.1:4321",
    ]

    GROQ_API_KEY: Optional[SecretStr] = None
    OPENAI_API_KEY: Optional[SecretStr] = None
    GEMINI_API_KEY: Optional[SecretStr] = None
    OPENROUTER_API_KEY: Optional[SecretStr] = None
    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "llama-3.1-8b-instant"

    ETL_INTERVAL_HOURS: int = 6

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")


settings = Settings()
