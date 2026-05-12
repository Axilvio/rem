from datetime import UTC, datetime

from sqlalchemy import BigInteger, DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SubscriptionUser(Base):
    __tablename__ = "subscription_users"
    __table_args__ = (UniqueConstraint("telegram_id", name="uq_subscription_users_telegram_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    telegram_username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    remnawave_username: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    remnawave_user_uuid: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    remnawave_short_uuid: Mapped[str | None] = mapped_column(String(64), nullable=True)
    subscription_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    last_membership_check_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoke_reason: Mapped[str | None] = mapped_column(Text, nullable=True)


async def create_schema(engine) -> None:  # type: ignore[no-untyped-def]
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
