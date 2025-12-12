from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"

    # IRCTC RapidAPI
    IRCTC_API_KEY: str = ""
    RAPIDAPI_HOST: str = "irctc1.p.rapidapi.com"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Postgres
    POSTGRES_URI: str = "postgresql+asyncpg://user:password@localhost:5432/dbname"

    # HuggingFace LLM
    HF_API_KEY: str = ""
    HF_API_URL: str = "https://router.huggingface.co/v1/chat/completions"
    HF_MODEL_NAME: str = "meta-llama/Llama-3.1-8B-Instruct"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings():
    return Settings()
