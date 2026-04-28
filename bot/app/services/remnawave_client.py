from remnawave import RemnawaveSDK

from bot.app.config import get_settings


class RemnawaveService:
    def __init__(self) -> None:
        settings = get_settings()
        self._sdk = RemnawaveSDK(base_url=settings.panel_api_base_url, token=settings.panel_api_token)

    async def ensure_user(self, username: str, telegram_id: int, trial_days: int) -> str:
        created = await self._sdk.users.create_user(
            username=username,
            telegram_id=telegram_id,
            status="ACTIVE",
            traffic_limit_bytes=0,
            expire_at_days=trial_days,
        )
        return str(created.response.uuid)
