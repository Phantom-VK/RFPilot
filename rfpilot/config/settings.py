import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL")
    DEEPSEEK_MODEL: str = "deepseek-v4-flash"
    MAX_CONCURRENCY: int = 5      # semaphore limit
    MAX_CHUNK_SIZE: int = 2000
    QA_GROUP_SIZE: int = 5

settings = Settings()