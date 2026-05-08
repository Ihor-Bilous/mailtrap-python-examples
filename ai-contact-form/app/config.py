from functools import cached_property, lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mailtrap_api_token: str
    mail_from: str
    mail_from_name: str

    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    route_sales_email: str
    route_support_email: str
    route_partnerships_email: str
    route_default_email: str

    model_config = SettingsConfigDict(env_file=".env")

    @cached_property
    def routing_map(self) -> dict[str, str]:
        return {
            "sales": self.route_sales_email,
            "support": self.route_support_email,
            "partnership": self.route_partnerships_email,
            "other": self.route_default_email,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
