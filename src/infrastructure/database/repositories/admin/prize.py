import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlmodel import col

from application.admin.dto.prize import CreatePrizeCommand, PrizeAdminDTO, UpdatePrizeCommand
from application.admin.interface.repositories.prize import IPrizeAdminRepository
from domain.services.prize_status_sync import apply_sold_out_status_from_quantities
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
        return tuple(self._to_prize_admin_dto(prize=prize) for prize in result.scalars().all())

    async def create_prize(self, command: CreatePrizeCommand) -> PrizeAdminDTO:
        for _ in range(5):
            try:
                async with self._session.begin_nested():
                    prize = Prize(
                        code=self._generate_prize_code(),
                        prize_name=command.prize_name,
                        description=command.description,
                        image_attachment=command.image_attachment,
                        prize_type=command.prize_type,
                        receive_type=command.receive_type,
                        status=command.status,
                        cost_points=command.cost_points,
                        quantity_total=command.quantity_total,
                        quantity_claimed=0,
                        required_level=command.required_level,
                        sort_order=command.sort_order,
                        is_active=command.is_active,
                    )
                    self._session.add(prize)
                    await self._session.flush()
                return self._to_prize_admin_dto(prize=prize)
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

        apply_sold_out_status_from_quantities(prize=prize)
        await self._session.flush()
        return self._to_prize_admin_dto(prize=prize)

    @staticmethod
    def _generate_prize_code() -> str:
        return f"store_prize_{uuid.uuid4().hex[:12]}"

    @staticmethod
    def _to_prize_admin_dto(*, prize: Prize) -> PrizeAdminDTO:
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
        )


__all__ = ["PrizeAdminRepository"]
