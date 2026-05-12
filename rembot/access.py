import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from rembot.telegram_membership import is_allowed_member_status

logger = logging.getLogger(__name__)


async def is_chat_member(bot: Bot, chat_id: int | str, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    except (TelegramBadRequest, TelegramForbiddenError) as exc:
        logger.warning("Could not check Telegram membership for user_id=%s: %s", user_id, exc)
        return False

    return is_allowed_member_status(member.status, getattr(member, "is_member", None))
