from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScraperSettings(BaseSettings):
    SCRAPER_DB_PATH: str = "./scraper.db"
    BACKEND_URL: str = "http://backend:8000"
    BACKEND_API_KEY: str = ""
    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "llama-3.1-8b-instant"
    GROQ_API_KEY: SecretStr | None = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_ENDPOINT: str = "https://api.groq.com/openai/v1/chat/completions"
    OPENAI_API_KEY: SecretStr | None = None
    GEMINI_API_KEY: SecretStr | None = None
    OPENROUTER_API_KEY: SecretStr | None = None
    AREA_MATCHER_MODE: str = "regex"
    ETL_INTERVAL_HOURS: int = 6
    RULES_FILE: str | None = None

    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite+aiosqlite:///{self.SCRAPER_DB_PATH}"

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")


settings = ScraperSettings()
