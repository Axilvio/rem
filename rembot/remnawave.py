import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from rembot.config import Settings
from rembot.remnawave_payload import (
    RemnawavePayloadError,
    build_subscription_url,
    extract_internal_squad_uuids,
    extract_object,
    unwrap_response,
)

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
        uuids = extract_internal_squad_uuids(payload)
        if not uuids:
            raise RemnawaveError("No internal squads returned by Remnawave API")
        return uuids

    async def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        payload = await self._request("GET", f"/users/by-username/{username}")
        if payload is None:
            return None
        return self._extract_user(payload, "getting Remnawave user by username")

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
        return self._extract_user(payload, "creating Remnawave user")

    async def delete_user(self, remnawave_user_uuid: str) -> bool:
        payload = await self._request("DELETE", f"/users/{remnawave_user_uuid}")
        if payload is None:
            return True
        response = self._unwrap_response(payload)
        if isinstance(response, dict):
            return bool(response.get("isDeleted", True))
        return True

    def subscription_url(self, user: dict[str, Any]) -> str:
        url = build_subscription_url(user, self._settings.remnawave_sub_base_url)
        if not url:
            raise RemnawaveError("Remnawave user response does not contain subscription URL")
        return url

    @staticmethod
    def make_remnawave_username(telegram_id: int) -> str:
        return f"tg_{telegram_id}"

    @staticmethod
    def _description(telegram_id: int, telegram_username: str | None) -> str:
        username = f"@{telegram_username}" if telegram_username else "без username"
        return f"Telegram bot user: {telegram_id} ({username})"

    @staticmethod
    def _unwrap_response(payload: Any) -> Any:
        return unwrap_response(payload)

    @classmethod
    def _extract_user(cls, payload: Any, action: str) -> dict[str, Any]:
        try:
            return extract_object(payload, action)
        except RemnawavePayloadError as exc:
            raise RemnawaveError(str(exc)) from exc
