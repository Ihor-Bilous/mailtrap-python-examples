from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mailtrap_api_token: str
    mailtrap_account_id: str

    mail_from: str
    mail_from_name: str
    alert_recipient_email: str

    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    poll_interval_minutes: int = 1
    event_retention_hours: int = 24
    bounce_rate_threshold: float = 0.05
    complaint_rate_threshold: float = 0.001
    open_rate_threshold: float = 0.20
    min_sample_size: int = 10
    alert_cooldown_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
