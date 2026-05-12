import logging
from typing import Literal

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

logger = logging.getLogger(__name__)

AllowedMembership = Literal["creator", "administrator", "member"]
ALLOWED_STATUSES: set[str] = {"creator", "administrator", "member"}
DENIED_STATUSES: set[str] = {"left", "kicked", "restricted"}


async def is_chat_member(bot: Bot, chat_id: int | str, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    except (TelegramBadRequest, TelegramForbiddenError) as exc:
        logger.warning("Could not check Telegram membership for user_id=%s: %s", user_id, exc)
        return False
    return member.status in ALLOWED_STATUSES
