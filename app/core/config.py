"""앱 설정 모듈.

pydantic-settings로 환경 변수를 로드합니다.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 앱 메타
    app_title: str = "FinBridge GraphRAG API"
    app_version: str = "0.1.0"
    app_description: str = "주가·재무 데이터 조회 및 AI 기반 금융 리서치 질의응답 API"
    debug: bool = False

    # PostgreSQL (DB 담당자가 설정)
    database_url: str = Field(default="", description="PostgreSQL connection string.")
    database_pool_size: int = 1
    database_max_overflow: int = 3
    database_echo: bool = False


@lru_cache
def get_settings() -> Settings:
    """설정 싱글톤을 반환합니다."""
    return Settings()
