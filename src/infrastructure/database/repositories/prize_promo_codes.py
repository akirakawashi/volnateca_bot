from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlmodel import col

from application.common.dto.prize_promo_code import (
    PrizePromoCodeBulkCreateResult,
    PrizePromoCodeRecord,
    PrizePromoCodeStats,
    normalize_prize_promo_codes,
)
from application.interface.repositories.prize_promo_codes import IPrizePromoCodeRepository
from application.common.dto.store import STORE_ALLOWED_PRIZE_TYPES
from domain.enums.prize import PrizePromoCodeStatus, PrizeStatus
from domain.services.prize_status_sync import apply_sold_out_status_from_quantities
from infrastructure.database.models.prize_promo_codes import PrizePromoCode
from infrastructure.database.models.prizes import Prize
from infrastructure.database.repositories.base import SQLAlchemyRepository


class PrizePromoCodeRepository(SQLAlchemyRepository, IPrizePromoCodeRepository):
    async def get_available_for_update(
        self,
        *,
        prizes_id: int,
    ) -> PrizePromoCodeRecord | None:
        result = await self._session.execute(
            select(PrizePromoCode)
            .where(
                col(PrizePromoCode.prizes_id) == prizes_id,
                col(PrizePromoCode.status) == PrizePromoCodeStatus.AVAILABLE,
            )
            .order_by(col(PrizePromoCode.prize_promo_codes_id))
            .with_for_update(skip_locked=True)
            .limit(1),
        )
        code = result.scalar_one_or_none()
        if code is None:
            return None
        return self._to_record(code=code)

    async def assign_to_redemption(
        self,
        *,
        prize_promo_codes_id: int,
        prize_redemptions_id: int,
        users_id: int,
        assigned_at: datetime,
    ) -> PrizePromoCodeRecord:
        result = await self._session.execute(
            select(PrizePromoCode)
            .where(col(PrizePromoCode.prize_promo_codes_id) == prize_promo_codes_id)
            .with_for_update(),
        )
        code = result.scalar_one_or_none()
        if code is None:
            raise RuntimeError(f"Промокод приза не найден: id={prize_promo_codes_id}")
        if code.status != PrizePromoCodeStatus.AVAILABLE:
            raise RuntimeError(f"Промокод приза уже назначен: id={prize_promo_codes_id}")

        code.status = PrizePromoCodeStatus.ASSIGNED
        code.prize_redemptions_id = prize_redemptions_id
        code.assigned_to_users_id = users_id
        code.assigned_at = assigned_at
        await self._session.flush()
        return self._to_record(code=code)

    async def get_stats(
        self,
        *,
        prizes_id: int,
    ) -> PrizePromoCodeStats:
        total_codes = await self._count(prizes_id=prizes_id, status=None)
        available_codes = await self._count(prizes_id=prizes_id, status=PrizePromoCodeStatus.AVAILABLE)
        assigned_codes = await self._count(prizes_id=prizes_id, status=PrizePromoCodeStatus.ASSIGNED)
        void_codes = await self._count(prizes_id=prizes_id, status=PrizePromoCodeStatus.VOID)
        return PrizePromoCodeStats(
            prizes_id=prizes_id,
            total_codes=total_codes,
            available_codes=available_codes,
            assigned_codes=assigned_codes,
            void_codes=void_codes,
        )

    async def bulk_create(
        self,
        *,
        prizes_id: int,
        promo_codes: tuple[str, ...],
    ) -> PrizePromoCodeBulkCreateResult | None:
        result = await self._session.execute(
            select(Prize).where(col(Prize.prizes_id) == prizes_id).with_for_update(),
        )
        prize = result.scalar_one_or_none()
        if prize is None:
            return None
        if prize.prize_type not in STORE_ALLOWED_PRIZE_TYPES:
            raise ValueError("Коды можно загрузить только для приза магазина")

        normalized_codes = normalize_prize_promo_codes(promo_codes)
        duplicates = len(promo_codes) - len(normalized_codes)
        created = 0

        for promo_code in normalized_codes:
            try:
                async with self._session.begin_nested():
                    self._session.add(
                        PrizePromoCode(
                            prizes_id=prizes_id,
                            promo_code=promo_code,
                            status=PrizePromoCodeStatus.AVAILABLE,
                        ),
                    )
                    await self._session.flush()
            except IntegrityError:
                duplicates += 1
            else:
                created += 1

        stats = await self.get_stats(prizes_id=prizes_id)
        await self._sync_prize_from_code_stats(prize=prize, stats=stats)
        return PrizePromoCodeBulkCreateResult(
            prizes_id=prizes_id,
            created=created,
            duplicates=duplicates,
            total_codes=stats.total_codes,
            available_codes=stats.available_codes,
            assigned_codes=stats.assigned_codes,
            void_codes=stats.void_codes,
        )

    async def _count(
        self,
        *,
        prizes_id: int,
        status: PrizePromoCodeStatus | None,
    ) -> int:
        query = select(func.count()).select_from(PrizePromoCode).where(
            col(PrizePromoCode.prizes_id) == prizes_id,
        )
        if status is not None:
            query = query.where(col(PrizePromoCode.status) == status)
        result = await self._session.execute(query)
        return int(result.scalar_one())

    async def _sync_prize_from_code_stats(
        self,
        *,
        prize: Prize,
        stats: PrizePromoCodeStats,
    ) -> None:
        prize.quantity_total = max(1, stats.total_codes)
        prize.quantity_claimed = stats.assigned_codes
        if stats.available_codes == 0 and prize.status != PrizeStatus.HIDDEN:
            prize.status = PrizeStatus.SOLD_OUT
        elif stats.available_codes > 0:
            apply_sold_out_status_from_quantities(prize=prize)
        await self._session.flush()

    @staticmethod
    def _to_record(*, code: PrizePromoCode) -> PrizePromoCodeRecord:
        if code.prize_promo_codes_id is None:
            raise RuntimeError("Первичный ключ промокода приза не был сгенерирован")

        return PrizePromoCodeRecord(
            prize_promo_codes_id=code.prize_promo_codes_id,
            prizes_id=code.prizes_id,
            promo_code=code.promo_code,
            status=code.status,
            prize_redemptions_id=code.prize_redemptions_id,
            assigned_to_users_id=code.assigned_to_users_id,
            assigned_at=code.assigned_at,
        )


__all__ = ["PrizePromoCodeRepository"]
