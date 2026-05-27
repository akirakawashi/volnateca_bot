from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import col

from application.interface.repositories.referral_intents import IReferralIntentRepository
from infrastructure.database.models.vk_referral_intents import VKReferralIntent
from infrastructure.database.repositories.base import SQLAlchemyRepository


class ReferralIntentRepository(SQLAlchemyRepository, IReferralIntentRepository):
    async def create_if_absent(
        self,
        *,
        invited_vk_user_id: int,
        raw_ref: str,
    ) -> None:
        clean_ref = raw_ref.strip()
        if not clean_ref:
            return

        statement = (
            insert(VKReferralIntent)
            .values(
                invited_vk_user_id=invited_vk_user_id,
                raw_ref=clean_ref,
            )
            .on_conflict_do_nothing(index_elements=["invited_vk_user_id"])
        )
        await self._session.execute(statement)
        await self._session.flush()

    async def get_raw_ref(
        self,
        *,
        invited_vk_user_id: int,
    ) -> str | None:
        result = await self._session.execute(
            select(VKReferralIntent).where(
                col(VKReferralIntent.invited_vk_user_id) == invited_vk_user_id,
            ),
        )
        intent = result.scalar_one_or_none()
        return intent.raw_ref if intent is not None else None

    async def delete_by_invited_vk_user_id(
        self,
        *,
        invited_vk_user_id: int,
    ) -> None:
        await self._session.execute(
            delete(VKReferralIntent).where(
                col(VKReferralIntent.invited_vk_user_id) == invited_vk_user_id,
            ),
        )
        await self._session.flush()
