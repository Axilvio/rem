import logging
from datetime import UTC, datetime

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, ChatMemberUpdated, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from rembot.access import is_chat_member
from rembot.config import Settings
from rembot.keyboards import start_keyboard, subscription_keyboard
from rembot.models import SubscriptionUser
from rembot.notify import notify_admin
from rembot.remnawave import RemnawaveClient, RemnawaveError

logger = logging.getLogger(__name__)
router = Router(name="rembot")



@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я выдаю подписку Remnawave участникам закрытого чата.\n\n"
        "Нажми кнопку ниже, чтобы получить свою подписку.",
        reply_markup=start_keyboard(),
    )


@router.callback_query(F.data == "get_subscription")
async def get_subscription_callback(
    callback: CallbackQuery,
    bot: Bot,
    settings: Settings,
    sessionmaker: async_sessionmaker[AsyncSession],
    remnawave: RemnawaveClient,
) -> None:
    await callback.answer("Проверяю доступ…")
    if callback.from_user is None:
        return

    user_id = callback.from_user.id
    telegram_username = callback.from_user.username
    allowed = await is_chat_member(bot, settings.target_chat_id, user_id)
    if not allowed:
        await callback.message.answer(  # type: ignore[union-attr]
            "⛔ Доступ запрещён. Подписка выдаётся только участникам чата."
        )
        await notify_admin(
            bot,
            settings,
            f"⛔ Попытка доступа без членства: {user_id} (@{telegram_username or 'нет'})",
        )
        return

    try:
        async with sessionmaker() as session:
            subscription = await ensure_subscription(
                session=session,
                remnawave=remnawave,
                telegram_id=user_id,
                telegram_username=telegram_username,
            )
            await session.commit()
    except RemnawaveError:
        logger.exception("Failed to issue subscription for telegram_id=%s", user_id)
        await callback.message.answer(  # type: ignore[union-attr]
            "⚠️ Не удалось выдать подписку из-за ошибки панели. Администратор уже уведомлён."
        )
        await notify_admin(bot, settings, f"⚠️ Ошибка Remnawave при выдаче подписки: {user_id}")
        return

    text = (
        "✅ Ваша подписка готова.\n\n"
        "Лимит трафика: без ограничений\n"
        "Лимит устройств: 2\n\n"
        f"<code>{subscription.subscription_url}</code>"
    )
    await callback.message.answer(  # type: ignore[union-attr]
        text,
        reply_markup=subscription_keyboard(subscription.subscription_url or ""),
        disable_web_page_preview=True,
    )
    await notify_admin(
        bot,
        settings,
        f"✅ Выдана подписка: {user_id} (@{telegram_username or 'нет'})",
    )


@router.my_chat_member()
async def bot_membership_changed(event: ChatMemberUpdated, settings: Settings) -> None:
    logger.info(
        "Bot membership changed in chat_id=%s from=%s to=%s target_chat=%s",
        event.chat.id,
        event.old_chat_member.status,
        event.new_chat_member.status,
        settings.target_chat_id,
    )


async def ensure_subscription(
    session: AsyncSession,
    remnawave: RemnawaveClient,
    telegram_id: int,
    telegram_username: str | None,
) -> SubscriptionUser:
    existing = await session.scalar(
        select(SubscriptionUser).where(SubscriptionUser.telegram_id == telegram_id)
    )
    if existing and existing.active and existing.subscription_url:
        existing.telegram_username = telegram_username
        existing.last_membership_check_at = datetime.now(UTC)
        return existing

    rem_user = await remnawave.create_or_get_user(telegram_id, telegram_username)
    sub_url = remnawave.subscription_url(rem_user)
    rem_username = remnawave.make_remnawave_username(telegram_id)

    if existing is None:
        existing = SubscriptionUser(
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            remnawave_username=rem_username,
        )
        session.add(existing)

    existing.telegram_username = telegram_username
    existing.remnawave_username = rem_username
    existing.remnawave_user_uuid = str(rem_user.get("uuid") or "")
    existing.remnawave_short_uuid = str(rem_user.get("shortUuid") or "")
    existing.subscription_url = sub_url
    existing.active = True
    existing.revoked_at = None
    existing.revoke_reason = None
    existing.last_membership_check_at = datetime.now(UTC)
    return existing


@router.chat_member()
async def group_member_changed(
    event: ChatMemberUpdated,
    bot: Bot,
    settings: Settings,
    sessionmaker: async_sessionmaker[AsyncSession],
    remnawave: RemnawaveClient,
) -> None:
    if str(event.chat.id) != str(settings.target_chat_id):
        return
    user = event.new_chat_member.user
    old_allowed = _chat_member_update_is_member(event.old_chat_member)
    new_allowed = _chat_member_update_is_member(event.new_chat_member)
    if old_allowed and not new_allowed:
        async with sessionmaker() as session:
            subscription = await session.scalar(
                select(SubscriptionUser).where(
                    SubscriptionUser.telegram_id == user.id,
                    SubscriptionUser.active.is_(True),
                )
            )
            if subscription:
                await revoke_subscription(
                    session=session,
                    remnawave=remnawave,
                    subscription=subscription,
                    reason=f"Пользователь вышел из чата: {event.new_chat_member.status}",
                )
                await session.commit()
                await notify_admin(
                    bot,
                    settings,
                    (
                        "🗑 Подписка удалена после выхода из чата: "
                        f"{user.id} (@{user.username or 'нет'})"
                    ),
                )


def _chat_member_update_is_member(member: object) -> bool:
    status = getattr(member, "status", None)
    if status in {"creator", "administrator", "member"}:
        return True
    if status == "restricted":
        return bool(getattr(member, "is_member", False))
    return False


async def revoke_subscription(
    session: AsyncSession,
    remnawave: RemnawaveClient,
    subscription: SubscriptionUser,
    reason: str,
) -> None:
    if subscription.remnawave_user_uuid:
        await remnawave.delete_user(subscription.remnawave_user_uuid)
    subscription.active = False
    subscription.revoked_at = datetime.now(UTC)
    subscription.revoke_reason = reason
    subscription.subscription_url = None
    await session.flush()
