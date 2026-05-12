from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(min_length=20)
    target_chat_id: int | str
    admin_chat_id: int | str | None = None

    remnawave_base_url: str
    remnawave_token: str = Field(min_length=10)
    remnawave_sub_base_url: str | None = None

    database_url: str = "sqlite+aiosqlite:///./rembot.sqlite3"
    membership_check_interval_seconds: int = Field(default=1800, ge=60)
    http_timeout_seconds: float = Field(default=20.0, ge=1.0)
    http_retries: int = Field(default=3, ge=1)

    @field_validator("bot_token", "remnawave_token")
    @classmethod
    def reject_placeholders(cls, value: str) -> str:
        if "replace-with" in value.lower():
            raise ValueError("secret value is not configured")
        return value

    @field_validator("remnawave_base_url", "remnawave_sub_base_url")
    @classmethod
    def trim_url(cls, value: str | None) -> str | None:
        if value and not value.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return value.rstrip("/") if value else value


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
