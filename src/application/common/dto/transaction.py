from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class TransactionRecord:
    """Запись из таблицы transactions, возвращаемая ITransactionRepository."""

    transactions_id: int
    users_id: int
    tasks_id: int | None
    amount: int
    balance_before: int
    balance_after: int
