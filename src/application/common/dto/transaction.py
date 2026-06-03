from dataclasses import dataclass
from datetime import datetime

from domain.enums.transaction import TransactionSource, TransactionType


@dataclass(slots=True, frozen=True, kw_only=True)
class TransactionRecord:
    """Запись из таблицы transactions, возвращаемая ITransactionRepository."""

    transactions_id: int
    users_id: int
    tasks_id: int | None
    amount: int
    balance_before: int
    balance_after: int


@dataclass(slots=True, frozen=True, kw_only=True)
class TransactionListRecord:
    """Полная запись транзакции для списков и админки."""

    transactions_id: int
    users_id: int
    tasks_id: int | None
    prizes_id: int | None
    transaction_type: TransactionType
    transaction_source: TransactionSource
    amount: int
    balance_before: int
    balance_after: int
    description: str | None
    created_at: datetime


__all__ = ["TransactionListRecord", "TransactionRecord"]
