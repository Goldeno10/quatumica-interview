from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/urlshortener"
    rate_limit_requests: int = 10
    rate_limit_window_seconds: int = 60
    auto_slug_length: int = 8


settings = Settings()
