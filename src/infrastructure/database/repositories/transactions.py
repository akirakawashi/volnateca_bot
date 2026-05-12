from datetime import datetime

from sqlalchemy import func, select
from sqlmodel import col

from application.common.dto.transaction import TransactionRecord
from application.interface.repositories.transactions import ITransactionRepository, MonthlyTopUserRecord
from domain.enums.transaction import TransactionSource, TransactionType
from infrastructure.database.models.achievements import Achievement
from infrastructure.database.models.transactions import Transaction
from infrastructure.database.models.user_achievements import UserAchievement
from infrastructure.database.models.users import User
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
            raise RuntimeError("Первичный ключ транзакции не был сгенерирован")

        return TransactionRecord(
            transactions_id=transaction.transactions_id,
            users_id=transaction.users_id,
            tasks_id=transaction.tasks_id,
            amount=transaction.amount,
            balance_before=transaction.balance_before,
            balance_after=transaction.balance_after,
        )

    async def list_top_accrual_users_for_period(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
        limit: int,
        excluded_achievement_code: str | None = None,
    ) -> tuple[MonthlyTopUserRecord, ...]:
        monthly_points = func.sum(Transaction.amount).label("monthly_points")
        conditions = [
            col(User.is_active).is_(True),
            col(Transaction.transaction_type) == TransactionType.ACCRUAL,
            col(Transaction.created_at) >= start_at,
            col(Transaction.created_at) < end_at,
        ]
        if excluded_achievement_code is not None:
            excluded_transactions = (
                select(col(UserAchievement.transactions_id))
                .join(
                    Achievement,
                    col(UserAchievement.achievements_id) == col(Achievement.achievements_id),
                )
                .where(col(Achievement.code) == excluded_achievement_code)
            )
            conditions.append(col(Transaction.transactions_id).not_in(excluded_transactions))

        result = await self._session.execute(
            select(
                col(User.users_id),
                col(User.vk_user_id),
                monthly_points,
            )
            .join(Transaction, col(Transaction.users_id) == col(User.users_id))
            .where(*conditions)
            .group_by(col(User.users_id), col(User.vk_user_id))
            .having(monthly_points > 0)
            .order_by(monthly_points.desc(), col(User.users_id))
            .limit(limit),
        )

        return tuple(
            MonthlyTopUserRecord(
                users_id=users_id,
                vk_user_id=vk_user_id,
                points=points,
            )
            for users_id, vk_user_id, points in result.all()
        )
