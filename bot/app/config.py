from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str = Field(alias="BOT_TOKEN")
    bot_admin_ids: str = Field(alias="BOT_ADMIN_IDS")
    bot_webhook_secret: str = Field(alias="BOT_WEBHOOK_SECRET")
    bot_db_dsn: str = Field(alias="BOT_DB_DSN")
    panel_api_base_url: str = Field(alias="PANEL_API_BASE_URL")
    panel_api_token: str = Field(alias="PANEL_API_TOKEN")
    trial_days: int = Field(default=2, alias="TRIAL_DAYS")
    payment_provider: str = Field(default="cryptomus", alias="PAYMENT_PROVIDER")
    cryptomus_webhook_secret: str = Field(default="", alias="CRYPTOMUS_WEBHOOK_SECRET")
    cryptocloud_api_key: str = Field(default="", alias="CRYPTOCLOUD_API_KEY")
    oxapay_api_key: str = Field(default="", alias="OXAPAY_API_KEY")


@lru_cache
def get_settings() -> Settings:
    return Settings()
