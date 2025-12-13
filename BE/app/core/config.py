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
    POSTGRES_URI: str = ""
    # HuggingFace LLM
    HF_API_KEY: str = ""
    HF_API_URL: str = "https://router.huggingface.co/v1/chat/completions"
    HF_MODEL_NAME: str = "meta-llama/Llama-3.1-8B-Instruct"

    SECRET_KEY:str =""
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 60
    REFRESH_TOKEN_EXPIRE_DAYS:int = 7
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings():
    return Settings()
