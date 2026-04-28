from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from admin.app.config import get_settings

engine = create_async_engine(get_settings().bot_db_dsn, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
