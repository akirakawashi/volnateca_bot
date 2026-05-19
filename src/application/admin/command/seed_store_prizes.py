from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from application.base_interactor import Interactor
from domain.enums.prize import PrizeReceiveType, PrizeStatus, PrizeType
from infrastructure.database.models.prizes import Prize
from utils.vk_attachments import normalize_vk_photo_attachment

STORE_PRIZE_IMAGE_ATTACHMENT_SOURCE = "photo-213947338_457239022%2Falbum-213947338_0%2Frev"
STORE_PRIZE_IMAGE_ATTACHMENT = (
    normalize_vk_photo_attachment(STORE_PRIZE_IMAGE_ATTACHMENT_SOURCE) or STORE_PRIZE_IMAGE_ATTACHMENT_SOURCE
)


@dataclass(slots=True, frozen=True, kw_only=True)
class StorePrizeFixture:
    code: str
    prize_name: str
    description: str
    prize_type: PrizeType
    receive_type: PrizeReceiveType
    status: PrizeStatus
    cost_points: int
    quantity_total: int | None
    quantity_claimed: int
    sort_order: int
    required_level: int | None = None


STORE_PRIZE_FIXTURES: tuple[StorePrizeFixture, ...] = (
    StorePrizeFixture(
        code="dev_store_sticker_pack",
        prize_name="Набор стикеров Волны",
        description="Плотные виниловые стикеры для ноутбука, блокнота или бутылки.",
        prize_type=PrizeType.MERCH,
        receive_type=PrizeReceiveType.PICKUP,
        status=PrizeStatus.AVAILABLE,
        cost_points=60,
        quantity_total=100,
        quantity_claimed=7,
        sort_order=10,
    ),
    StorePrizeFixture(
        code="dev_store_tshirt",
        prize_name="Футболка Волнатеки",
        description="Базовая футболка с символикой проекта. Размер уточняется при выдаче.",
        prize_type=PrizeType.MERCH,
        receive_type=PrizeReceiveType.PICKUP,
        status=PrizeStatus.AVAILABLE,
        cost_points=120,
        quantity_total=20,
        quantity_claimed=3,
        sort_order=20,
    ),
    StorePrizeFixture(
        code="dev_store_bottle",
        prize_name="Бутылка для воды",
        description="Многоразовая бутылка для тренировок и поездок.",
        prize_type=PrizeType.MERCH,
        receive_type=PrizeReceiveType.PICKUP,
        status=PrizeStatus.AVAILABLE,
        cost_points=180,
        quantity_total=15,
        quantity_claimed=0,
        sort_order=30,
    ),
    StorePrizeFixture(
        code="dev_store_tote_bag",
        prize_name="Шоппер Волны",
        description="Тканевый шоппер из тестовой партии.",
        prize_type=PrizeType.MERCH,
        receive_type=PrizeReceiveType.PICKUP,
        status=PrizeStatus.SOLD_OUT,
        cost_points=240,
        quantity_total=10,
        quantity_claimed=10,
        sort_order=40,
    ),
    StorePrizeFixture(
        code="dev_store_partner_coffee",
        prize_name="Кофе у партнёра",
        description="Сертификат на напиток у партнёра проекта.",
        prize_type=PrizeType.PARTNER,
        receive_type=PrizeReceiveType.MANAGER_CONTACT,
        status=PrizeStatus.AVAILABLE,
        cost_points=90,
        quantity_total=50,
        quantity_claimed=4,
        sort_order=50,
    ),
    StorePrizeFixture(
        code="dev_store_partner_certificate",
        prize_name="Сертификат партнёра",
        description="Тестовый партнёрский сертификат для ручной проверки магазина.",
        prize_type=PrizeType.PARTNER,
        receive_type=PrizeReceiveType.MANAGER_CONTACT,
        status=PrizeStatus.AVAILABLE,
        cost_points=350,
        quantity_total=8,
        quantity_claimed=0,
        sort_order=60,
    ),
    StorePrizeFixture(
        code="dev_store_partner_workshop",
        prize_name="Мастер-класс партнёра",
        description="Место на партнёрском мастер-классе. Детали уточнит менеджер.",
        prize_type=PrizeType.PARTNER,
        receive_type=PrizeReceiveType.MANAGER_CONTACT,
        status=PrizeStatus.AVAILABLE,
        cost_points=800,
        quantity_total=3,
        quantity_claimed=0,
        sort_order=70,
        required_level=2,
    ),
    StorePrizeFixture(
        code="dev_store_super_speaker",
        prize_name="Портативная колонка",
        description="Суперприз в одном экземпляре.",
        prize_type=PrizeType.SUPER_PRIZE,
        receive_type=PrizeReceiveType.MANAGER_CONTACT,
        status=PrizeStatus.AVAILABLE,
        cost_points=1500,
        quantity_total=1,
        quantity_claimed=0,
        sort_order=80,
        required_level=3,
    ),
    StorePrizeFixture(
        code="dev_store_super_headphones",
        prize_name="Беспроводные наушники",
        description="Суперприз, который уже разобрали. Нужен для проверки sold out состояния.",
        prize_type=PrizeType.SUPER_PRIZE,
        receive_type=PrizeReceiveType.MANAGER_CONTACT,
        status=PrizeStatus.SOLD_OUT,
        cost_points=2200,
        quantity_total=1,
        quantity_claimed=1,
        sort_order=90,
    ),
    StorePrizeFixture(
        code="dev_store_super_trip",
        prize_name="Большой финальный приз",
        description="Дорогой суперприз для проверки состояния нехватки баллов.",
        prize_type=PrizeType.SUPER_PRIZE,
        receive_type=PrizeReceiveType.MANAGER_CONTACT,
        status=PrizeStatus.AVAILABLE,
        cost_points=5000,
        quantity_total=1,
        quantity_claimed=0,
        sort_order=100,
        required_level=4,
    ),
)


@dataclass(slots=True, frozen=True, kw_only=True)
class SeedStorePrizesCommand:
    pass


@dataclass(slots=True, frozen=True, kw_only=True)
class SeedStorePrizesDTO:
    messages: tuple[str, ...]


class SeedStorePrizesHandler(Interactor[SeedStorePrizesCommand, SeedStorePrizesDTO]):
    """Засеивает dev-призы магазина идемпотентно по code."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __call__(self, command_data: SeedStorePrizesCommand) -> SeedStorePrizesDTO:
        del command_data

        codes = tuple(fixture.code for fixture in STORE_PRIZE_FIXTURES)
        result = await self._session.execute(select(Prize).where(col(Prize.code).in_(codes)))
        existing_by_code = {prize.code: prize for prize in result.scalars().all()}

        created = 0
        updated = 0
        messages: list[str] = []

        try:
            for fixture in STORE_PRIZE_FIXTURES:
                prize = existing_by_code.get(fixture.code)
                if prize is None:
                    prize = Prize(code=fixture.code)
                    self._session.add(prize)
                    created += 1
                    action = "created"
                else:
                    updated += 1
                    action = "updated"

                _apply_fixture(prize=prize, fixture=fixture)
                messages.append(f"{action}: {fixture.code} — {fixture.prize_name}")

            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

        return SeedStorePrizesDTO(
            messages=(
                f"Seeded store prizes: created={created}, updated={updated}",
                f"image_attachment={STORE_PRIZE_IMAGE_ATTACHMENT}",
                *messages,
            ),
        )


def _apply_fixture(*, prize: Prize, fixture: StorePrizeFixture) -> None:
    prize.prize_name = fixture.prize_name
    prize.description = fixture.description
    prize.image_attachment = STORE_PRIZE_IMAGE_ATTACHMENT
    prize.prize_type = fixture.prize_type
    prize.receive_type = fixture.receive_type
    prize.status = fixture.status
    prize.cost_points = fixture.cost_points
    prize.quantity_total = fixture.quantity_total
    prize.quantity_claimed = fixture.quantity_claimed
    prize.required_level = fixture.required_level
    prize.sort_order = fixture.sort_order
    prize.is_active = True


__all__ = [
    "SeedStorePrizesCommand",
    "SeedStorePrizesDTO",
    "SeedStorePrizesHandler",
]
