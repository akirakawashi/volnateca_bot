from application.common.dto.transaction import TransactionRecord
from application.interface.repositories.transactions import ITransactionRepository
from domain.enums.transaction import TransactionSource, TransactionType
from infrastructure.database.models.transactions import Transaction
from infrastructure.database.repositories.base import SQLAlchemyRepository


class TransactionRepository(SQLAlchemyRepository, ITransactionRepository):
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
        transaction = Transaction(
            users_id=users_id,
            tasks_id=tasks_id,
            prizes_id=prizes_id,
            transaction_type=transaction_type,
            transaction_source=transaction_source,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
        )
        self._session.add(transaction)
        await self._session.flush()
        if transaction.transactions_id is None:
            raise RuntimeError("Transaction primary key was not generated")

        return TransactionRecord(
            transactions_id=transaction.transactions_id,
            users_id=transaction.users_id,
            tasks_id=transaction.tasks_id,
            amount=transaction.amount,
            balance_before=transaction.balance_before,
            balance_after=transaction.balance_after,
        )
