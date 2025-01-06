import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(".env")) if Path(".env").exists() else None,
        env_file_encoding='utf-8'
    )

    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_TEST_URL: str = os.getenv("DATABASE_TEST_URL")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")