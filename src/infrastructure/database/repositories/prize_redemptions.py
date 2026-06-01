from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from sqlmodel import col

from application.common.dto.prize_redemption import CreatePrizeRedemptionParams, PrizeRedemptionRecord
from application.common.exceptions import PrizeRedemptionIdempotencyConflict
from application.common.redemption_code import generate_redemption_code
from application.interface.repositories.prize_redemptions import IPrizeRedemptionRepository
from domain.enums.prize import PrizeRedemptionStatus
from infrastructure.database.models.prize_redemptions import PrizeRedemption
from infrastructure.database.models.prizes import Prize
from infrastructure.database.models.users import User
from infrastructure.database.repositories.base import SQLAlchemyRepository

_MAX_REDEMPTION_CODE_INSERT_ATTEMPTS = 3


class PrizeRedemptionRepository(SQLAlchemyRepository, IPrizeRedemptionRepository):
    async def get_by_idempotency_key(
        self,
        *,
        idempotency_key: str,
    ) -> PrizeRedemptionRecord | None:
        result = await self._session.execute(
            select(PrizeRedemption, Prize.prize_name)
            .join(Prize, col(Prize.prizes_id) == col(PrizeRedemption.prizes_id))
            .where(col(PrizeRedemption.idempotency_key) == idempotency_key),
        )
        row = result.one_or_none()
        if row is None:
            return None
        redemption, prize_name = row
        return self._to_record(redemption=redemption, prize_name=prize_name)

    async def get_by_id(
        self,
        *,
        prize_redemptions_id: int,
    ) -> PrizeRedemptionRecord | None:
        return await self._get_record(
            prize_redemptions_id=prize_redemptions_id,
            for_update=False,
        )

    async def get_for_update(
        self,
        *,
        prize_redemptions_id: int,
    ) -> PrizeRedemptionRecord | None:
        return await self._get_record(
            prize_redemptions_id=prize_redemptions_id,
            for_update=True,
        )

    async def create(
        self,
        params: CreatePrizeRedemptionParams,
    ) -> PrizeRedemptionRecord:
        redemption_code = params.redemption_code
        redemption: PrizeRedemption | None = None

        for attempt in range(_MAX_REDEMPTION_CODE_INSERT_ATTEMPTS):
            try:
                async with self._session.begin_nested():
                    redemption = PrizeRedemption(
                        users_id=params.users_id,
                        prizes_id=params.prizes_id,
                        transactions_id=params.transactions_id,
                        receive_type=params.receive_type,
                        redemption_code=redemption_code,
                        idempotency_key=params.idempotency_key,
                        points_spent=params.points_spent,
                        comment=params.comment,
                        prize_redemption_status=PrizeRedemptionStatus.RESERVED,
                    )
                    self._session.add(redemption)
                    await self._session.flush()
            except IntegrityError:
                existing = await self.get_by_idempotency_key(
                    idempotency_key=params.idempotency_key,
                )
                if existing is not None:
                    raise PrizeRedemptionIdempotencyConflict(existing=existing) from None
                if attempt + 1 >= _MAX_REDEMPTION_CODE_INSERT_ATTEMPTS:
                    raise
                redemption_code = generate_redemption_code()
                continue
            else:
                break

        if redemption is None:
            raise RuntimeError("Не удалось создать заявку на приз")

        prize_name = await self._get_prize_name(prizes_id=params.prizes_id)
        return self._to_record(redemption=redemption, prize_name=prize_name)

    async def list_by_user(
        self,
        *,
        users_id: int,
        limit: int,
        offset: int,
    ) -> tuple[PrizeRedemptionRecord, ...]:
        result = await self._session.execute(
            select(PrizeRedemption, Prize.prize_name)
            .join(Prize, col(Prize.prizes_id) == col(PrizeRedemption.prizes_id))
            .where(col(PrizeRedemption.users_id) == users_id)
            .order_by(col(PrizeRedemption.created_at).desc())
            .limit(max(1, limit))
            .offset(max(0, offset)),
        )
        return tuple(
            self._to_record(redemption=redemption, prize_name=prize_name)
            for redemption, prize_name in result.all()
        )

    async def list_for_fulfillment(
        self,
        *,
        status: PrizeRedemptionStatus | None,
        prizes_id: int | None,
        limit: int,
        offset: int,
    ) -> tuple[PrizeRedemptionRecord, ...]:
        user_alias = aliased(User)
        query = (
            select(PrizeRedemption, Prize.prize_name, user_alias.vk_user_id)
            .join(Prize, col(Prize.prizes_id) == col(PrizeRedemption.prizes_id))
            .join(user_alias, col(user_alias.users_id) == col(PrizeRedemption.users_id))
            .order_by(col(PrizeRedemption.created_at).desc())
            .limit(max(1, limit))
            .offset(max(0, offset))
        )
        if status is not None:
            query = query.where(col(PrizeRedemption.prize_redemption_status) == status)
        if prizes_id is not None:
            query = query.where(col(PrizeRedemption.prizes_id) == prizes_id)

        result = await self._session.execute(query)
        return tuple(
            self._to_record(
                redemption=redemption,
                prize_name=prize_name,
                vk_user_id=vk_user_id,
            )
            for redemption, prize_name, vk_user_id in result.all()
        )

    async def mark_issued(
        self,
        *,
        prize_redemptions_id: int,
        issued_at: datetime,
        comment: str | None,
    ) -> PrizeRedemptionRecord:
        redemption = await self._get_entity_for_update(prize_redemptions_id=prize_redemptions_id)
        redemption.prize_redemption_status = PrizeRedemptionStatus.ISSUED
        redemption.issued_at = issued_at
        if comment is not None:
            redemption.comment = comment
        await self._session.flush()
        prize_name = await self._get_prize_name(prizes_id=redemption.prizes_id)
        return self._to_record(redemption=redemption, prize_name=prize_name)

    async def mark_canceled(
        self,
        *,
        prize_redemptions_id: int,
        canceled_at: datetime,
        cancel_reason: str | None,
        refund_transactions_id: int,
    ) -> PrizeRedemptionRecord:
        redemption = await self._get_entity_for_update(prize_redemptions_id=prize_redemptions_id)
        redemption.prize_redemption_status = PrizeRedemptionStatus.CANCELED
        redemption.canceled_at = canceled_at
        redemption.cancel_reason = cancel_reason
        redemption.refund_transactions_id = refund_transactions_id
        await self._session.flush()
        prize_name = await self._get_prize_name(prizes_id=redemption.prizes_id)
        return self._to_record(redemption=redemption, prize_name=prize_name)

    async def _get_record(
        self,
        *,
        prize_redemptions_id: int,
        for_update: bool,
    ) -> PrizeRedemptionRecord | None:
        query = (
            select(PrizeRedemption, Prize.prize_name, User.vk_user_id)
            .join(Prize, col(Prize.prizes_id) == col(PrizeRedemption.prizes_id))
            .join(User, col(User.users_id) == col(PrizeRedemption.users_id))
            .where(col(PrizeRedemption.prize_redemptions_id) == prize_redemptions_id)
        )
        if for_update:
            query = query.with_for_update(of=PrizeRedemption)

        result = await self._session.execute(query)
        row = result.one_or_none()
        if row is None:
            return None
        redemption, prize_name, vk_user_id = row
        return self._to_record(
            redemption=redemption,
            prize_name=prize_name,
            vk_user_id=vk_user_id,
        )

    async def _get_entity_for_update(self, *, prize_redemptions_id: int) -> PrizeRedemption:
        result = await self._session.execute(
            select(PrizeRedemption)
            .where(col(PrizeRedemption.prize_redemptions_id) == prize_redemptions_id)
            .with_for_update(),
        )
        redemption = result.scalar_one_or_none()
        if redemption is None:
            raise RuntimeError(f"Заявка на приз не найдена: id={prize_redemptions_id}")
        return redemption

    async def _get_prize_name(self, *, prizes_id: int) -> str:
        result = await self._session.execute(
            select(Prize.prize_name).where(col(Prize.prizes_id) == prizes_id),
        )
        prize_name = result.scalar_one_or_none()
        return prize_name if prize_name is not None else ""

    @staticmethod
    def _to_record(
        *,
        redemption: PrizeRedemption,
        prize_name: str | None,
        vk_user_id: int | None = None,
    ) -> PrizeRedemptionRecord:
        if redemption.prize_redemptions_id is None:
            raise RuntimeError("Первичный ключ заявки на приз не был сгенерирован")
        if redemption.transactions_id is None:
            raise RuntimeError("Заявка на приз должна быть связана с транзакцией списания")

        return PrizeRedemptionRecord(
            prize_redemptions_id=redemption.prize_redemptions_id,
            users_id=redemption.users_id,
            prizes_id=redemption.prizes_id,
            transactions_id=redemption.transactions_id,
            prize_redemption_status=redemption.prize_redemption_status,
            receive_type=redemption.receive_type,
            redemption_code=redemption.redemption_code,
            idempotency_key=redemption.idempotency_key,
            points_spent=redemption.points_spent,
            comment=redemption.comment,
            issued_at=redemption.issued_at,
            canceled_at=redemption.canceled_at,
            cancel_reason=redemption.cancel_reason,
            refund_transactions_id=redemption.refund_transactions_id,
            created_at=redemption.created_at,
            prize_name=prize_name,
            vk_user_id=vk_user_id,
        )


__all__ = ["PrizeRedemptionRepository"]
