from abc import ABC, abstractmethod

from application.common.dto.transaction import TransactionRecord
from domain.enums.transaction import TransactionSource, TransactionType


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
