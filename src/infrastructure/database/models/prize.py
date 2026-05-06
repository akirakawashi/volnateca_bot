from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, Text, func
from sqlmodel import Column, Field, Relationship

from infrastructure.database.base import BaseModel, enum_values

if TYPE_CHECKING:
    from infrastructure.database.models.transaction import Transaction


class PrizeType(str, Enum):
    MERCH = "merch"
    PROMO_CODE = "promo_code"
    SUPER_PRIZE = "super_prize"
    PARTNER = "partner"


class PrizeReceiveType(str, Enum):
    PICKUP = "pickup"
    DELIVERY = "delivery"
    PROMO_CODE = "promo_code"
    MANAGER_CONTACT = "manager_contact"


class PrizeStatus(str, Enum):
    AVAILABLE = "available"
    SOLD_OUT = "sold_out"
    HIDDEN = "hidden"


class Prize(BaseModel, table=True):
    """
    Справочник призов магазина.

    Хранит стоимость, остатки и способ получения приза. Суперпризы
    представлены тем же справочником, но с ограниченным количеством.
    """

    __tablename__ = "prize"

    prize_id: int | None = Field(default=None, primary_key=True)
    code: str = Field(
        nullable=False,
        unique=True,
        index=True,
        description="Стабильный уникальный код приза для seed-данных, логики приложения и админки",
    )
    title: str = Field(nullable=False, description="Название приза для пользователя")
    description: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="Подробное описание приза",
    )
    prize_type: PrizeType = Field(
        sa_column=Column(
            SAEnum(PrizeType, name="prize_type", values_callable=enum_values),
            nullable=False,
        ),
        description="Категория приза: мерч, промокод, суперприз или партнёрский приз",
    )
    receive_type: PrizeReceiveType = Field(
        sa_column=Column(
            SAEnum(
                PrizeReceiveType, name="prize_receive_type", values_callable=enum_values
            ),
            nullable=False,
        ),
        description="Сценарий выдачи приза: самовывоз, доставка, промокод или связь с менеджером",
    )
    status: PrizeStatus = Field(
        default=PrizeStatus.AVAILABLE,
        sa_column=Column(
            SAEnum(PrizeStatus, name="prize_status", values_callable=enum_values),
            nullable=False,
        ),
        description="Статус доступности приза для отображения и покупки в магазине",
    )
    cost_points: int = Field(
        nullable=False, index=True, description="Стоимость получения приза в очках"
    )
    quantity_total: int | None = Field(
        default=None,
        description="Общее количество доступных единиц приза; NULL означает, что остаток не ограничивается системой",
    )
    quantity_claimed: int = Field(
        default=0,
        nullable=False,
        description="Количество единиц приза, уже выданных или зарезервированных пользователями",
    )
    sort_order: int = Field(
        default=0, nullable=False, description="Порядок отображения в магазине"
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
        index=True,
        description="Показывать ли приз в магазине",
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

    transactions: list["Transaction"] = Relationship(back_populates="prize")
