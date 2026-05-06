from enum import Enum


class PrizeType(str, Enum):
    """Категория приза в магазине."""

    MERCH = "merch"  # Мерч Волны
    PROMO_CODE = "promo_code"  # Промокод партнера
    SUPER_PRIZE = "super_prize"  # Штучный суперприз
    PARTNER = "partner"  # Партнерский приз без промокода


class PrizeReceiveType(str, Enum):
    """Способ получения или выдачи приза."""

    PICKUP = "pickup"  # Самовывоз
    DELIVERY = "delivery"  # Доставка
    PROMO_CODE = "promo_code"  # Отправка промокода в боте
    MANAGER_CONTACT = "manager_contact"  # Связь с менеджером


class PrizeStatus(str, Enum):
    """Статус доступности приза в магазине."""

    AVAILABLE = "available"  # Доступен для получения
    SOLD_OUT = "sold_out"  # Разобрали
    HIDDEN = "hidden"  # Скрыт из магазина


class PrizeRedemptionStatus(str, Enum):
    """Статус пользовательской заявки на приз."""

    RESERVED = "reserved"  # Приз зарезервирован за пользователем
    ISSUED = "issued"  # Приз выдан или промокод отправлен
    CANCELED = "canceled"  # Заявка отменена


class PromoCodeStatus(str, Enum):
    """Статус конкретного промокода партнёрского приза."""

    AVAILABLE = "available"  # Можно выдать пользователю
    RESERVED = "reserved"  # Временно закреплён за заявкой
    ISSUED = "issued"  # Отправлен пользователю
    DISABLED = "disabled"  # Отключён и не должен выдаваться


__all__ = [
    "PromoCodeStatus",
    "PrizeReceiveType",
    "PrizeRedemptionStatus",
    "PrizeStatus",
    "PrizeType",
]
