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
    ACHIEVEMENT = "achievement"  # Бонус за достижение или игровое правило
    ADJUSTMENT = "adjustment"  # Ручная корректировка баланса администратором


__all__ = [
    "TransactionSource",
    "TransactionType",
]
