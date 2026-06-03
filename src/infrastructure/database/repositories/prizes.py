from sqlalchemy import func, select, update
from sqlmodel import col

from application.common.dto.prize_redemption import PrizeLockedSnapshot
from application.common.dto.store import STORE_ALLOWED_PRIZE_TYPES, StorePrizeSnapshot
from application.interface.repositories.prizes import IPrizeRepository
from domain.enums.prize import PrizeStatus, PrizeType
from domain.services.prize_status_sync import apply_sold_out_status_from_quantities
from infrastructure.database.models.prizes import Prize
from infrastructure.database.repositories.base import SQLAlchemyRepository


class PrizeRepository(SQLAlchemyRepository, IPrizeRepository):
    async def list_store_prizes(
        self,
        *,
        prize_types: tuple[PrizeType, ...],
        limit: int,
        offset: int,
    ) -> tuple[StorePrizeSnapshot, ...]:
        if not prize_types or limit <= 0:
            return ()

        result = await self._session.execute(
            select(Prize)
            .where(
                col(Prize.is_active).is_(True),
                col(Prize.status) != PrizeStatus.HIDDEN,
                col(Prize.prize_type).in_(prize_types),
            )
            .order_by(
                col(Prize.sort_order),
                col(Prize.cost_points),
                col(Prize.prizes_id),
            )
            .limit(limit)
            .offset(max(0, offset)),
        )
        return tuple(self._to_store_prize_snapshot(prize=prize) for prize in result.scalars().all())

    async def count_store_prizes(
        self,
        *,
        prize_types: tuple[PrizeType, ...],
    ) -> int:
        if not prize_types:
            return 0

        result = await self._session.execute(
            select(func.count())
            .select_from(Prize)
            .where(
                col(Prize.is_active).is_(True),
                col(Prize.status) != PrizeStatus.HIDDEN,
                col(Prize.prize_type).in_(prize_types),
            ),
        )
        return int(result.scalar_one())

    async def get_store_prize(
        self,
        *,
        prizes_id: int,
    ) -> StorePrizeSnapshot | None:
        result = await self._session.execute(
            select(Prize).where(
                col(Prize.prizes_id) == prizes_id,
                col(Prize.is_active).is_(True),
                col(Prize.status) != PrizeStatus.HIDDEN,
                col(Prize.prize_type).in_(STORE_ALLOWED_PRIZE_TYPES),
            ),
        )
        prize = result.scalar_one_or_none()
        if prize is None:
            return None
        return self._to_store_prize_snapshot(prize=prize)

    async def get_for_update(
        self,
        *,
        prizes_id: int,
    ) -> PrizeLockedSnapshot | None:
        result = await self._session.execute(
            select(Prize).where(col(Prize.prizes_id) == prizes_id).with_for_update(),
        )
        prize = result.scalar_one_or_none()
        if prize is None or prize.prizes_id is None:
            return None
        return self._to_locked_snapshot(prize=prize)

    async def try_increment_claimed(
        self,
        *,
        prizes_id: int,
    ) -> bool:
        result = await self._session.execute(
            update(Prize)
            .where(col(Prize.prizes_id) == prizes_id)
            .where(col(Prize.quantity_claimed) < col(Prize.quantity_total))
            .values(quantity_claimed=Prize.quantity_claimed + 1),
        )
        return result.rowcount == 1

    async def decrement_claimed(
        self,
        *,
        prizes_id: int,
    ) -> None:
        await self._session.execute(
            update(Prize)
            .where(col(Prize.prizes_id) == prizes_id)
            .where(col(Prize.quantity_claimed) > 0)
            .values(quantity_claimed=Prize.quantity_claimed - 1),
        )
        await self._session.flush()

    async def sync_sold_out_status(
        self,
        *,
        prizes_id: int,
    ) -> None:
        result = await self._session.execute(
            select(Prize).where(col(Prize.prizes_id) == prizes_id).with_for_update(),
        )
        prize = result.scalar_one_or_none()
        if prize is None:
            return
        apply_sold_out_status_from_quantities(prize=prize)
        await self._session.flush()

    @staticmethod
    def _to_locked_snapshot(*, prize: Prize) -> PrizeLockedSnapshot:
        if prize.prizes_id is None:
            raise RuntimeError("Первичный ключ приза не был сгенерирован")

        return PrizeLockedSnapshot(
            prizes_id=prize.prizes_id,
            code=prize.code,
            prize_name=prize.prize_name,
            prize_type=prize.prize_type,
            receive_type=prize.receive_type,
            status=prize.status,
            cost_points=prize.cost_points,
            quantity_total=prize.quantity_total,
            quantity_claimed=prize.quantity_claimed,
            required_level=prize.required_level,
            is_active=prize.is_active,
        )

    @staticmethod
    def _to_store_prize_snapshot(*, prize: Prize) -> StorePrizeSnapshot:
        if prize.prizes_id is None:
            raise RuntimeError("Первичный ключ приза не был сгенерирован")

        return StorePrizeSnapshot(
            prizes_id=prize.prizes_id,
            prize_name=prize.prize_name,
            description=prize.description,
            image_attachment=prize.image_attachment,
            prize_type=prize.prize_type,
            status=prize.status,
            cost_points=prize.cost_points,
            quantity_total=prize.quantity_total,
            quantity_claimed=prize.quantity_claimed,
            sort_order=prize.sort_order,
            required_level=prize.required_level,
        )


__all__ = ["PrizeRepository"]
