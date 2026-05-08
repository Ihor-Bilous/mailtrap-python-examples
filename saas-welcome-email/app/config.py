from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mailtrap_api_token: str
    mailtrap_template_uuid: str
    mailtrap_env: str = "sandbox"
    mailtrap_sandbox_inbox_id: str = ""

    mail_from: str
    mail_from_name: str

    gemini_api_key: str
    gemini_model: str = "gemini-3.1-flash"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def is_sandbox(self) -> bool:
        return self.mailtrap_env.lower() == "sandbox"


@lru_cache
def get_settings() -> Settings:
    return Settings()
