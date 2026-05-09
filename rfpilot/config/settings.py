"""Application settings loaded from environment variables."""

import os

# pylint: disable=import-error
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Runtime settings for API credentials and pipeline limits."""

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL")
    DEEPSEEK_MODEL: str = "deepseek-v4-flash"
    AGENT_RUN_TIMEOUT_SECONDS: int = 120
    MAX_CONCURRENCY: int = 7
    MAX_CHUNK_SIZE: int = 1200
    MAP_CHUNK_BATCH_SIZE: int = 15
    QA_GROUP_SIZE: int = 5

settings = Settings()
