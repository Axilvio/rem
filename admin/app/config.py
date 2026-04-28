from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    admin_secret_key: str = Field(alias="ADMIN_SECRET_KEY")
    admin_db_dsn: str = Field(alias="ADMIN_DB_DSN")
    admin_api_token: str = Field(alias="ADMIN_API_TOKEN")
    bot_db_dsn: str = Field(alias="BOT_DB_DSN")


@lru_cache
def get_settings() -> Settings:
    return Settings()
