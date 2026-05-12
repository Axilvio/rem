import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from rembot.config import Settings

logger = logging.getLogger(__name__)


class RemnawaveError(RuntimeError):
    pass


class RemnawaveClient:
    def __init__(self, settings: Settings) -> None:
        base_url = settings.remnawave_base_url.rstrip("/")
        if not base_url.endswith("/api"):
            base_url = f"{base_url}/api"
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {settings.remnawave_token}"},
            timeout=settings.http_timeout_seconds,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        last_error: Exception | None = None
        for attempt in range(1, self._settings.http_retries + 1):
            try:
                response = await self._client.request(method, url, **kwargs)
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                if response.content:
                    return response.json()
                return None
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                if attempt >= self._settings.http_retries:
                    break
                await asyncio.sleep(min(2**attempt, 8))
        msg = f"Remnawave API request failed: {method} {url}: {last_error}"
        raise RemnawaveError(msg) from last_error

    async def get_all_internal_squad_uuids(self) -> list[str]:
        payload = await self._request("GET", "/internal-squads")
        squads = payload.get("internalSquads", []) if isinstance(payload, dict) else []
        uuids = [str(squad["uuid"]) for squad in squads if squad.get("uuid")]
        if not uuids:
            raise RemnawaveError("No internal squads returned by Remnawave API")
        return uuids

    async def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        payload = await self._request("GET", f"/users/by-username/{username}")
        return payload if isinstance(payload, dict) else None

    async def create_or_get_user(
        self, telegram_id: int, telegram_username: str | None
    ) -> dict[str, Any]:
        username = self.make_remnawave_username(telegram_id)
        existing = await self.get_user_by_username(username)
        if existing:
            return existing

        squads = await self.get_all_internal_squad_uuids()
        expire_at = datetime.now(UTC) + timedelta(days=365 * 20)
        body: dict[str, Any] = {
            "username": username,
            "expireAt": expire_at.isoformat(),
            "status": "ACTIVE",
            "trafficLimitStrategy": "NO_RESET",
            "trafficLimitBytes": 0,
            "telegramId": telegram_id,
            "hwidDeviceLimit": 2,
            "activeInternalSquads": squads,
            "description": self._description(telegram_id, telegram_username),
            "tag": "TELEGRAM",
        }
        payload = await self._request("POST", "/users", json=body)
        if not isinstance(payload, dict):
            raise RemnawaveError("Unexpected empty response when creating Remnawave user")
        return payload

    async def delete_user(self, remnawave_user_uuid: str) -> bool:
        payload = await self._request("DELETE", f"/users/{remnawave_user_uuid}")
        if payload is None:
            return True
        if isinstance(payload, dict):
            return bool(payload.get("isDeleted", True))
        return True

    def subscription_url(self, user: dict[str, Any]) -> str:
        short_uuid = user.get("shortUuid") or user.get("short_uuid")
        if self._settings.remnawave_sub_base_url and short_uuid:
            return f"{self._settings.remnawave_sub_base_url.rstrip('/')}/{short_uuid}"
        url = user.get("subscriptionUrl") or user.get("subscription_url")
        if not url:
            raise RemnawaveError("Remnawave user response does not contain subscription URL")
        return str(url)

    @staticmethod
    def make_remnawave_username(telegram_id: int) -> str:
        return f"tg_{telegram_id}"

    @staticmethod
    def _description(telegram_id: int, telegram_username: str | None) -> str:
        username = f"@{telegram_username}" if telegram_username else "без username"
        return f"Telegram bot user: {telegram_id} ({username})"
