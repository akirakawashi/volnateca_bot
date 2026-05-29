from application.common.dto.store import (
    StoreCatalogDTO,
    StorePrizeCardDTO,
    StorePrizeUserState,
    StorePrizeView,
)
from domain.enums.prize import PrizeType
from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages._template import (
    VKMessageText,
    _template_message,
)


def build_store_root_message(*, balance_points: int) -> VKMessageText:
    return VKMessageText(
        text=(
            "🎁 Магазин призов\n\n"
            f"💫 Баланс: {balance_points} ✦\n\n"
            "Выбери раздел каталога:"
        ),
    )


def build_store_catalog_message(*, catalog: StoreCatalogDTO) -> VKMessageText:
    header = (
        f"🎁 Магазин · {catalog.section.label}\n\n"
        f"💫 Баланс: {catalog.balance_points} ✦\n"
        f"Страница {catalog.pagination.page} из {catalog.pagination.total_pages}"
    )
    if not catalog.prizes:
        return VKMessageText(text=f"{header}\n\nВ этом разделе пока нет призов.")

    start_index = (catalog.pagination.page - 1) * catalog.pagination.page_size
    prize_blocks = [
        _build_store_catalog_prize_line(index=start_index + index, prize=prize)
        for index, prize in enumerate(catalog.prizes, start=1)
    ]
    return VKMessageText(text=f"{header}\n\n" + "\n\n".join(prize_blocks))


def build_store_catalog_navigation_message(*, catalog: StoreCatalogDTO) -> VKMessageText:
    return _template_message(
        "store_catalog_navigation",
        section_label=catalog.section.label,
        page=catalog.pagination.page,
        total_pages=catalog.pagination.total_pages,
    )


def build_store_catalog_carousel_message(*, catalog: StoreCatalogDTO) -> VKMessageText:
    return _template_message(
        "store_catalog_carousel",
        section_label=catalog.section.label,
        total_items=catalog.pagination.total_items,
        balance_points=catalog.balance_points,
        page=catalog.pagination.page,
        total_pages=catalog.pagination.total_pages,
    )


def build_store_exit_message() -> VKMessageText:
    return VKMessageText(text="Главное меню")


def build_store_prize_card_message(*, card: StorePrizeCardDTO) -> VKMessageText:
    prize = card.prize
    if prize is None:
        return build_store_prize_not_found_message()

    description = _format_optional_description(prize.description)
    return VKMessageText(
        text=(
            f"🎁 {prize.prize_name}\n"
            f"{_format_prize_type(prize.prize_type)}\n\n"
            f"Стоимость: {prize.cost_points} ✦\n"
            f"Баланс: {card.balance_points} ✦\n"
            f"Статус: {_format_store_prize_state(prize)}\n"
            f"Остаток: {_format_prize_quantity(prize)}"
            f"{description}"
        ),
    )


def build_store_prize_not_found_message() -> VKMessageText:
    return VKMessageText(text="🎁 Магазин призов\n\nЭтот приз уже недоступен в каталоге.")


def build_store_claim_unavailable_message(*, prize_name: str | None) -> VKMessageText:
    title = f"🎁 {prize_name}" if prize_name else "🎁 Магазин призов"
    return VKMessageText(
        text=(
            f"{title}\n\n"
            "Получение призов пока не подключено.\n"
            "Каталог уже можно смотреть, баллы не списываются."
        ),
    )


def _build_store_catalog_prize_line(*, index: int, prize: StorePrizeView) -> str:
    return (
        f"{index}. {prize.prize_name}\n"
        f"{prize.cost_points} ✦ · {_format_store_prize_state(prize)}"
    )


def _format_store_prize_state(prize: StorePrizeView) -> str:
    if prize.user_state == StorePrizeUserState.AVAILABLE:
        return "доступен"
    if prize.user_state == StorePrizeUserState.INSUFFICIENT_BALANCE:
        return f"не хватает {prize.missing_points} ✦"
    if prize.user_state == StorePrizeUserState.LEVEL_LOCKED:
        required_level = prize.required_level if prize.required_level is not None else "выше"
        return f"нужен уровень {required_level}"
    return "разобрали"


def _format_prize_quantity(prize: StorePrizeView) -> str:
    if prize.user_state == StorePrizeUserState.SOLD_OUT:
        return "разобрали"
    if prize.quantity_total is None:
        return "без ограничения"
    return f"{prize.quantity_remaining} из {prize.quantity_total}"


def _format_prize_type(prize_type: PrizeType) -> str:
    if prize_type == PrizeType.MERCH:
        return "Мерч"
    if prize_type == PrizeType.PARTNER:
        return "Партнёрский приз"
    if prize_type == PrizeType.SUPER_PRIZE:
        return "Суперприз"
    return "Приз"


def _format_optional_description(description: str | None) -> str:
    clean_description = description.strip() if description is not None else ""
    if not clean_description:
        return ""
    return f"\n\n{clean_description}"
