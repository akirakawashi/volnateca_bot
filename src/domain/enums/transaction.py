from enum import Enum


class TransactionType(str, Enum):
    """Направление движения баланса пользователя."""

    ACCRUAL = "accrual"  # Начисление очков пользователю
    SPEND = "spend"  # Списание очков с баланса пользователя


class TransactionSource(str, Enum):
    """Бизнес-причина появления транзакции."""

    REGISTRATION = "registration"  # Бонус за регистрацию в боте
    TASK = "task"  # Начисление или корректировка по заданию
    PRIZE = "prize"  # Списание за приз или возврат очков по призу
    REFERRAL = "referral"  # Бонус за приглашенного пользователя
    ADJUSTMENT = "adjustment"  # Ручная корректировка баланса администратором


class TransactionStatus(str, Enum):
    """Статус применения транзакции к балансу."""

    PENDING = "pending"  # Операция ожидает обработки
    COMPLETED = "completed"  # Операция применена к балансу
    CANCELED = "canceled"  # Операция отменена


__all__ = [
    "TransactionSource",
    "TransactionStatus",
    "TransactionType",
]
