import logging

from aiogram import Bot

from rembot.config import Settings

logger = logging.getLogger(__name__)


async def notify_admin(bot: Bot, settings: Settings, text: str) -> None:
    if settings.admin_chat_id is None:
        return
    try:
        await bot.send_message(
            chat_id=settings.admin_chat_id, text=text, disable_web_page_preview=True
        )
    except Exception:
        logger.exception("Failed to send admin notification")
