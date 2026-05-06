from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, Text, func
from sqlmodel import Column, Field, Relationship

from domain.enums.prize import PrizeReceiveType, PrizeStatus, PrizeType
from infrastructure.database.base import BaseModel, enum_values

if TYPE_CHECKING:
    from infrastructure.database.models.prize_promo_code import PrizePromoCode
    from infrastructure.database.models.prize_redemption import PrizeRedemption
    from infrastructure.database.models.transaction import Transaction


class Prize(BaseModel, table=True):
    """
    Справочник призов магазина.

    Хранит стоимость, остатки и способ получения приза. Суперпризы
    представлены тем же справочником, но с ограниченным количеством.
    """

    __tablename__ = "prize"
    __table_args__ = (
        CheckConstraint("cost_points > 0", name="cost_points_positive"),
        CheckConstraint(
            "quantity_claimed >= 0", name="quantity_claimed_non_negative"
        ),
        CheckConstraint(
            "quantity_total IS NULL OR quantity_claimed <= quantity_total",
            name="quantity_claimed_lte_quantity_total",
        ),
    )

    prize_id: int | None = Field(default=None, primary_key=True)
    code: str = Field(
        nullable=False,
        unique=True,
        index=True,
        description="Стабильный уникальный код приза для seed-данных, логики приложения и админки",
    )
    prize_name: str = Field(
        nullable=False, description="Название приза для пользователя"
    )
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
    sort_order: int = Field(  # TODO уточнить у Влада нужно ли
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

    promo_codes: list["PrizePromoCode"] = Relationship(back_populates="prize")
    prize_redemptions: list["PrizeRedemption"] = Relationship(back_populates="prize")
    transactions: list["Transaction"] = Relationship(back_populates="prize")
