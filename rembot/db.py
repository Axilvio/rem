from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from rembot.config import Settings


def make_engine(settings: Settings):  # type: ignore[no-untyped-def]
    return create_async_engine(settings.database_url, pool_pre_ping=True)


def make_sessionmaker(engine) -> async_sessionmaker[AsyncSession]:  # type: ignore[no-untyped-def]
    return async_sessionmaker(engine, expire_on_commit=False)


async def session_scope(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
