import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlmodel import col

from application.admin.command.prize import CreatePrizeCommand, UpdatePrizeCommand
from application.admin.dto.prize import PrizeAdminDTO
from application.admin.interface.repositories.prize import IPrizeAdminRepository
from application.common.dto.prize_promo_code import PrizePromoCodeStats
from domain.enums.prize import PrizePromoCodeStatus, PrizeReceiveType, PrizeStatus, PrizeType
from domain.services.prize_status_sync import apply_sold_out_status_from_quantities
from infrastructure.database.models.prize_promo_codes import PrizePromoCode
from infrastructure.database.models.prizes import Prize
from infrastructure.database.repositories.base import SQLAlchemyRepository


class PrizeAdminRepository(SQLAlchemyRepository, IPrizeAdminRepository):
    async def list_prizes(self) -> tuple[PrizeAdminDTO, ...]:
        result = await self._session.execute(
            select(Prize).order_by(
                col(Prize.sort_order),
                col(Prize.cost_points),
                col(Prize.prizes_id),
            ),
        )
        items: list[PrizeAdminDTO] = []
        for prize in result.scalars().all():
            stats = (
                await self._get_promo_code_stats(prizes_id=prize.prizes_id)
                if prize.prizes_id is not None
                else None
            )
            items.append(self._to_prize_admin_dto(prize=prize, promo_stats=stats))
        return tuple(items)

    async def create_prize(self, command: CreatePrizeCommand) -> PrizeAdminDTO:
        if command.prize_type == PrizeType.PARTNER:
            if command.receive_type != PrizeReceiveType.PROMO_CODE:
                raise ValueError("Партнёрский приз должен иметь receive_type promo_code")
            if command.status == PrizeStatus.AVAILABLE and not command.promo_codes:
                raise ValueError("Для доступного партнёрского приза нужно загрузить хотя бы один промокод")

        for _ in range(5):
            try:
                async with self._session.begin_nested():
                    quantity_total = (
                        max(1, len(command.promo_codes))
                        if command.prize_type == PrizeType.PARTNER
                        else command.quantity_total
                    )
                    prize = Prize(
                        code=self._generate_prize_code(),
                        prize_name=command.prize_name,
                        description=command.description,
                        image_attachment=command.image_attachment,
                        prize_type=command.prize_type,
                        receive_type=command.receive_type,
                        status=command.status,
                        cost_points=command.cost_points,
                        quantity_total=quantity_total,
                        quantity_claimed=0,
                        required_level=command.required_level,
                        sort_order=command.sort_order,
                        is_active=command.is_active,
                    )
                    self._session.add(prize)
                    await self._session.flush()
                    if prize.prizes_id is None:
                        raise RuntimeError("Первичный ключ приза не был сгенерирован")
                    for promo_code in command.promo_codes:
                        self._session.add(
                            PrizePromoCode(
                                prizes_id=prize.prizes_id,
                                promo_code=promo_code,
                                status=PrizePromoCodeStatus.AVAILABLE,
                            ),
                        )
                    await self._session.flush()
                stats = await self._get_promo_code_stats(prizes_id=prize.prizes_id)
                return self._to_prize_admin_dto(prize=prize, promo_stats=stats)
            except IntegrityError:
                continue

        raise RuntimeError("Не удалось сгенерировать уникальный код приза")

    async def update_prize(self, command: UpdatePrizeCommand) -> PrizeAdminDTO | None:
        result = await self._session.execute(
            select(Prize).where(col(Prize.prizes_id) == command.prizes_id).with_for_update(),
        )
        prize = result.scalar_one_or_none()
        if prize is None:
            return None

        if "prize_name" in command.fields:
            if command.prize_name is None:
                raise ValueError("prize_name не может быть пустым")
            prize.prize_name = command.prize_name
        if "description" in command.fields:
            prize.description = command.description
        if "image_attachment" in command.fields:
            prize.image_attachment = command.image_attachment
        if "status" in command.fields:
            if command.status is None:
                raise ValueError("status обязателен")
            prize.status = command.status
        if "cost_points" in command.fields:
            if command.cost_points is None:
                raise ValueError("cost_points обязателен")
            prize.cost_points = command.cost_points
        if "quantity_total" in command.fields:
            if prize.prize_type == PrizeType.PARTNER:
                raise ValueError("Количество партнёрского приза считается по загруженным промокодам")
            if command.quantity_total is None:
                raise ValueError("quantity_total обязателен")
            if command.quantity_total < prize.quantity_claimed:
                raise ValueError(
                    "quantity_total не может быть меньше уже зарезервированного количества "
                    f"({prize.quantity_claimed})",
                )
            prize.quantity_total = command.quantity_total
        if "required_level" in command.fields:
            prize.required_level = command.required_level
        if "sort_order" in command.fields:
            if command.sort_order is None:
                raise ValueError("sort_order обязателен")
            prize.sort_order = command.sort_order
        if "is_active" in command.fields:
            if command.is_active is None:
                raise ValueError("is_active обязателен")
            prize.is_active = command.is_active

        promo_stats = (
            await self._get_promo_code_stats(prizes_id=prize.prizes_id)
            if prize.prizes_id is not None
            else None
        )
        if (
            prize.prize_type == PrizeType.PARTNER
            and prize.status == PrizeStatus.AVAILABLE
            and (promo_stats is None or promo_stats.available_codes <= 0)
        ):
            raise ValueError("Нельзя сделать партнёрский приз доступным: загрузите свободные промокоды")

        if prize.status == PrizeStatus.AVAILABLE and prize.quantity_claimed >= prize.quantity_total:
            raise ValueError(
                "Нельзя сделать приз доступным: увеличьте количество больше уже занятого",
            )

        apply_sold_out_status_from_quantities(prize=prize)
        await self._session.flush()
        return self._to_prize_admin_dto(prize=prize, promo_stats=promo_stats)

    @staticmethod
    def _generate_prize_code() -> str:
        return f"store_prize_{uuid.uuid4().hex[:12]}"

    async def _get_promo_code_stats(self, *, prizes_id: int) -> PrizePromoCodeStats:
        total_codes = await self._count_promo_codes(prizes_id=prizes_id, status=None)
        available_codes = await self._count_promo_codes(
            prizes_id=prizes_id,
            status=PrizePromoCodeStatus.AVAILABLE,
        )
        assigned_codes = await self._count_promo_codes(
            prizes_id=prizes_id,
            status=PrizePromoCodeStatus.ASSIGNED,
        )
        void_codes = await self._count_promo_codes(
            prizes_id=prizes_id,
            status=PrizePromoCodeStatus.VOID,
        )
        return PrizePromoCodeStats(
            prizes_id=prizes_id,
            total_codes=total_codes,
            available_codes=available_codes,
            assigned_codes=assigned_codes,
            void_codes=void_codes,
        )

    async def _count_promo_codes(
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

    @staticmethod
    def _to_prize_admin_dto(
        *,
        prize: Prize,
        promo_stats: PrizePromoCodeStats | None = None,
    ) -> PrizeAdminDTO:
        if prize.prizes_id is None:
            raise RuntimeError("Первичный ключ приза не был сгенерирован")

        return PrizeAdminDTO(
            prizes_id=prize.prizes_id,
            code=prize.code,
            prize_name=prize.prize_name,
            description=prize.description,
            image_attachment=prize.image_attachment,
            prize_type=prize.prize_type,
            receive_type=prize.receive_type,
            status=prize.status,
            cost_points=prize.cost_points,
            quantity_total=prize.quantity_total,
            quantity_claimed=prize.quantity_claimed,
            required_level=prize.required_level,
            sort_order=prize.sort_order,
            is_active=prize.is_active,
            promo_codes_total=promo_stats.total_codes if promo_stats is not None else None,
            promo_codes_available=promo_stats.available_codes if promo_stats is not None else None,
            promo_codes_assigned=promo_stats.assigned_codes if promo_stats is not None else None,
            promo_codes_void=promo_stats.void_codes if promo_stats is not None else None,
        )


__all__ = ["PrizeAdminRepository"]
