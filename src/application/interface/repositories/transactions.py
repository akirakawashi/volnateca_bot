from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from application.common.dto.transaction import TransactionRecord
from domain.enums.transaction import TransactionSource, TransactionType


@dataclass(slots=True, frozen=True, kw_only=True)
class MonthlyTopUserRecord:
    users_id: int
    vk_user_id: int
    points: int


class ITransactionRepository(ABC):
    """Репозиторий журнала транзакций баланса пользователя.

    Отвечает только за вставку строк в таблицу transactions. Расчёт сумм
    и баланса до/после выполняет WalletService и AwardTaskService.
    """

    @abstractmethod
    async def create(
        self,
        *,
        users_id: int,
        tasks_id: int | None,
        prizes_id: int | None,
        transaction_type: TransactionType,
        transaction_source: TransactionSource,
        amount: int,
        balance_before: int,
        balance_after: int,
        description: str | None,
    ) -> TransactionRecord:
        raise NotImplementedError

    @abstractmethod
    async def list_top_accrual_users_for_period(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
        limit: int,
        excluded_achievement_code: str | None = None,
    ) -> tuple[MonthlyTopUserRecord, ...]:
        """Возвращает пользователей с максимальными начислениями за период."""
        raise NotImplementedError
