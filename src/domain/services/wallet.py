from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True, slots=True)
class AccrualResult:
    """Результат начисления очков пользователю.

    Содержит баланс до операции, после операции и накопленный итог.
    Используется оркестратором (AwardTaskService) для применения изменений
    к пользователю и записи транзакции в журнал.
    """

    amount: int
    balance_before: int
    balance_after: int
    earned_points_total_after: int


class WalletService:
    """Чистая доменная логика движения внутренней валюты пользователя.

    Сервис не знает про БД, ORM и инфраструктуру: на вход — примитивы текущего
    состояния пользователя и сумма операции, на выход — состояние после
    применения. Запись в БД остаётся ответственностью репозиториев и
    оркестратора (AwardTaskService).
    """

    @staticmethod
    def accrue(
        *,
        balance_before: int,
        earned_points_total_before: int,
        amount: int,
    ) -> AccrualResult:
        if amount <= 0:
            raise ValueError("Accrual amount must be positive")
        if balance_before < 0:
            raise ValueError("Balance before accrual must be non-negative")
        if earned_points_total_before < 0:
            raise ValueError("Earned points total must be non-negative")

        return AccrualResult(
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_before + amount,
            earned_points_total_after=earned_points_total_before + amount,
        )
