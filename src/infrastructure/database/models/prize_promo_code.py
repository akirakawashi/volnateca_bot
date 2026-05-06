from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum as SAEnum, func
from sqlmodel import Column, Field, Relationship

from domain.enums.prize import PromoCodeStatus
from infrastructure.database.base import BaseModel, enum_values

if TYPE_CHECKING:
    from infrastructure.database.models.prize import Prize
    from infrastructure.database.models.prize_redemption import PrizeRedemption


class PrizePromoCode(BaseModel, table=True):
    """
    Конкретный промокод для приза типа PROMO_CODE.

    Таблица хранит пул кодов, из которого бот атомарно выбирает доступный код,
    закрепляет его за заявкой и отправляет пользователю в сообщениях.
    """

    __tablename__ = "prize_promo_codes"

    prize_promo_codes_id: int | None = Field(default=None, primary_key=True)
    prize_id: int = Field(
        foreign_key="prize.prize_id",
        nullable=False,
        index=True,
        description="ID приза, к которому относится этот промокод",
    )
    prize_redemptions_id: int | None = Field(
        default=None,
        foreign_key="prize_redemptions.prize_redemptions_id",
        unique=True,
        description="ID заявки на приз, за которой закреплён промокод",
    )
    promo_code: str = Field(
        nullable=False,
        unique=True,
        index=True,
        description="Конкретное значение промокода, которое бот отправляет пользователю",
    )
    promo_code_status: PromoCodeStatus = Field(
        default=PromoCodeStatus.AVAILABLE,
        sa_column=Column(
            SAEnum(
                PromoCodeStatus,
                name="promo_code_status",
                values_callable=enum_values,
            ),
            index=True,
            nullable=False,
        ),
        description="Статус доступности конкретного промокода",
    )
    issued_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Дата и время отправки промокода пользователю",
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
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
    prize_redemption: Optional["PrizeRedemption"] = Relationship(
        back_populates="promo_code"
    )
