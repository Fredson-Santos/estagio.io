"""Configuracao do pacote compartilhado (somente leitura de variaveis de ambiente).

Usada por scrapers e extractor quando executados pelo servico scraper.
O backend da API usa sua propria configuracao (backend/app/core/config.py).
"""
from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SharedSettings(BaseSettings):
    DATABASE_URL: str

    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "llama-3.1-8b-instant"
    GROQ_API_KEY: Optional[SecretStr] = None
    OPENAI_API_KEY: Optional[SecretStr] = None
    GEMINI_API_KEY: Optional[SecretStr] = None
    OPENROUTER_API_KEY: Optional[SecretStr] = None

    ETL_INTERVAL_HOURS: int = 6

    RULES_FILE: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")


settings = SharedSettings()
