from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📲 Получить подписку", callback_data="get_subscription")],
        ]
    )


def subscription_keyboard(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Открыть подписку", url=url)],
            [
                InlineKeyboardButton(
                    text="📋 Получить ссылку ещё раз", callback_data="get_subscription"
                )
            ],
        ]
    )
