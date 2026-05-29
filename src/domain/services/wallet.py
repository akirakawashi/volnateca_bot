from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True, slots=True)
class AccrualResult:
    """Результат начисления очков пользователю."""

    amount: int
    balance_before: int
    balance_after: int
    earned_points_total_after: int


@dataclass(frozen=True, kw_only=True, slots=True)
class SpendResult:
    """Результат списания очков за приз."""

    amount: int
    balance_before: int
    balance_after: int
    spent_points_total_after: int


class WalletService:
    """Чистая доменная логика движения внутренней валюты пользователя."""

    @staticmethod
    def accrue(
        *,
        balance_before: int,
        earned_points_total_before: int,
        amount: int,
    ) -> AccrualResult:
        if amount <= 0:
            raise ValueError("Сумма начисления должна быть положительной")
        if balance_before < 0:
            raise ValueError("Баланс до начисления не может быть отрицательным")
        if earned_points_total_before < 0:
            raise ValueError("Суммарно заработанные баллы не могут быть отрицательными")

        return AccrualResult(
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_before + amount,
            earned_points_total_after=earned_points_total_before + amount,
        )

    @staticmethod
    def spend(
        *,
        balance_before: int,
        spent_points_total_before: int,
        amount: int,
    ) -> SpendResult:
        if amount <= 0:
            raise ValueError("Сумма списания должна быть положительной")
        if balance_before < 0:
            raise ValueError("Баланс до списания не может быть отрицательным")
        if spent_points_total_before < 0:
            raise ValueError("Суммарно потраченные баллы не могут быть отрицательными")
        if balance_before < amount:
            raise ValueError("Недостаточно баллов для списания")

        return SpendResult(
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_before - amount,
            spent_points_total_after=spent_points_total_before + amount,
        )

    @staticmethod
    def refund_spend(
        *,
        balance_before: int,
        spent_points_total_before: int,
        amount: int,
    ) -> SpendResult:
        if amount <= 0:
            raise ValueError("Сумма возврата должна быть положительной")
        if balance_before < 0:
            raise ValueError("Баланс до возврата не может быть отрицательным")
        if spent_points_total_before < amount:
            raise ValueError("Нельзя вернуть больше, чем было потрачено")

        return SpendResult(
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_before + amount,
            spent_points_total_after=spent_points_total_before - amount,
        )
