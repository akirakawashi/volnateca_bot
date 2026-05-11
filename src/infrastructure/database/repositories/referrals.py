from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlmodel import col

from application.interface.repositories.referrals import IReferralRepository
from infrastructure.database.models.referrals import Referral
from infrastructure.database.repositories.base import SQLAlchemyRepository


class ReferralRepository(SQLAlchemyRepository, IReferralRepository):
    """Репозиторий реферальных связей между пользователями."""

    async def create_if_not_exists(
        self,
        inviter_users_id: int,
        invited_users_id: int,
    ) -> tuple[int, bool]:
        try:
            async with self._session.begin_nested():
                referral = Referral(
                    inviter_users_id=inviter_users_id,
                    invited_users_id=invited_users_id,
                )
                self._session.add(referral)
                await self._session.flush()
        except IntegrityError:
            result = await self._session.execute(
                select(Referral).where(col(Referral.invited_users_id) == invited_users_id),
            )
            existing = result.scalar_one()
            return existing.referrals_id, False  # type: ignore[return-value]

        return referral.referrals_id, True  # type: ignore[return-value]

    async def count_referrals(self, inviter_users_id: int) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(Referral)
            .where(
                col(Referral.inviter_users_id) == inviter_users_id,
            ),
        )
        return result.scalar_one()

    async def set_bonus_transaction(
        self,
        referrals_id: int,
        transactions_id: int,
    ) -> None:
        result = await self._session.execute(
            select(Referral).where(col(Referral.referrals_id) == referrals_id),
        )
        referral = result.scalar_one_or_none()
        if referral is not None:
            referral.bonus_transactions_id = transactions_id
            self._session.add(referral)
