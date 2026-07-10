from enum import Enum


class PrizeType(str, Enum):
    """Категория приза в магазине."""

    MERCH = "merch"  # Мерч Волны
    PROMO_CODE = "promo_code"  # Устаревший тип промокода партнёра
    SUPER_PRIZE = "super_prize"  # Штучный суперприз
    PARTNER = "partner"  # Партнёрский приз


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


class PrizePromoCodeStatus(str, Enum):
    """Статус одноразового кода приза."""

    AVAILABLE = "available"  # Код свободен и может быть выдан покупателю
    ASSIGNED = "assigned"  # Код закреплён за заявкой и пользователем
    VOID = "void"  # Код выведен из оборота вручную


__all__ = [
    "PrizePromoCodeStatus",
    "PrizeReceiveType",
    "PrizeRedemptionStatus",
    "PrizeStatus",
    "PrizeType",
]
