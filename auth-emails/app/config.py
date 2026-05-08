from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    mailtrap_api_token: str
    mail_from: str
    mail_from_name: str
    base_url: str
    token_max_age_seconds: int = 3600

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
