from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum as SAEnum, Index, UniqueConstraint, func
from sqlmodel import Column, Field, Relationship

from domain.enums.prize import PrizePromoCodeStatus
from infrastructure.database.base import BaseModel, enum_values

if TYPE_CHECKING:
    from infrastructure.database.models.prize_redemptions import PrizeRedemption
    from infrastructure.database.models.prizes import Prize
    from infrastructure.database.models.users import User


class PrizePromoCode(BaseModel, table=True):
    """Одноразовый промокод партнёрского приза."""

    __tablename__ = "prize_promo_codes"
    __table_args__ = (
        UniqueConstraint("prizes_id", "promo_code", name="uq_prize_promo_codes_prizes_id_promo_code"),
        UniqueConstraint("prize_redemptions_id", name="uq_prize_promo_codes_prize_redemptions_id"),
        Index("ix_prize_promo_codes_prizes_id_status", "prizes_id", "status"),
    )

    prize_promo_codes_id: int | None = Field(default=None, primary_key=True)
    prizes_id: int = Field(
        foreign_key="prizes.prizes_id",
        nullable=False,
        index=True,
        description="ID партнёрского приза, к которому относится код",
    )
    promo_code: str = Field(nullable=False, description="Нормализованный промокод партнёра")
    status: PrizePromoCodeStatus = Field(
        default=PrizePromoCodeStatus.AVAILABLE,
        sa_column=Column(
            SAEnum(
                PrizePromoCodeStatus,
                name="prize_promo_code_status",
                values_callable=enum_values,
            ),
            nullable=False,
        ),
        description="Статус одноразового промокода",
    )
    prize_redemptions_id: int | None = Field(
        default=None,
        foreign_key="prize_redemptions.prize_redemptions_id",
        description="Заявка, которой назначен промокод",
    )
    assigned_to_users_id: int | None = Field(
        default=None,
        foreign_key="users.users_id",
        index=True,
        description="Пользователь, которому назначен промокод",
    )
    assigned_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Дата и время закрепления промокода за пользователем",
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )

    prize: "Prize" = Relationship(back_populates="promo_codes")
    redemption: Optional["PrizeRedemption"] = Relationship(back_populates="promo_code")
    assigned_to_user: Optional["User"] = Relationship()
