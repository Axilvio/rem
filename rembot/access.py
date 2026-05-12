import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

logger = logging.getLogger(__name__)
ALLOWED_STATUSES: set[str] = {"creator", "administrator", "member"}


async def is_chat_member(bot: Bot, chat_id: int | str, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    except (TelegramBadRequest, TelegramForbiddenError) as exc:
        logger.warning("Could not check Telegram membership for user_id=%s: %s", user_id, exc)
        return False

    if member.status in ALLOWED_STATUSES:
        return True
    if member.status == "restricted":
        return bool(getattr(member, "is_member", False))
    return False
