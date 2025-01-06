import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(".env")) if Path(".env").exists() else None,
        env_file_encoding='utf-8'
    )

    DATABASE_URL: str
    DATABASE_TEST_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str
    ALGORITHM: str