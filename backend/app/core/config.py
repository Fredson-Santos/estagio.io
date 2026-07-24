from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "estagio.io API"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str
    CORS_ORIGINS: list[str] = [
        "http://localhost:4321",
        "http://127.0.0.1:4321",
    ]
    ADMIN_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")


settings = Settings()
