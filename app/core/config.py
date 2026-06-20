from functools import lru_cache

from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(
        default="",
        description="Supabase Postgres connection string.",
    )
    database_pool_size: int = 1
    database_max_overflow: int = 3
    database_echo: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
