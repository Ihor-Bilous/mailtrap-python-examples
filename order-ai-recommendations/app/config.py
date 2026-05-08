from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mailtrap_api_token: str
    mailtrap_template_uuid: str = ""
    mail_from: str
    mail_from_name: str

    stripe_secret_key: str
    stripe_webhook_secret: str

    gemini_api_key: str

    order_recipient_email: str = ""

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
