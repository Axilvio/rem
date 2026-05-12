import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from rembot.config import get_settings
from rembot.db import make_engine, make_sessionmaker
from rembot.handlers import router
from rembot.logging import setup_logging
from rembot.models import create_schema
from rembot.remnawave import RemnawaveClient
from rembot.sync import MembershipSync

logger = logging.getLogger(__name__)


async def run_bot() -> None:
    setup_logging()
    settings = get_settings()
    engine = make_engine(settings)
    sessionmaker = make_sessionmaker(engine)
    await create_schema(engine)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    remnawave = RemnawaveClient(settings)
    sync = MembershipSync(bot, settings, sessionmaker, remnawave)

    dp["settings"] = settings
    dp["sessionmaker"] = sessionmaker
    dp["remnawave"] = remnawave
    dp.include_router(router)

    sync.start()
    try:
        logger.info("Starting bot polling")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logger.info("Stopping bot")
        await sync.stop()
        await remnawave.aclose()
        await bot.session.close()
        await engine.dispose()


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
