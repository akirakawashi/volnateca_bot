from application.command.list_user_redemptions import ListUserRedemptionsDTO
from application.common.dto.store import (
    StoreCatalogDTO,
    StorePrizeCardDTO,
    StorePrizeUserState,
    StorePrizeView,
)
from application.services.redeem_prize_service import RedeemPrizeOutcome, RedeemPrizeOutcomeStatus
from domain.enums.prize import PrizeRedemptionStatus, PrizeType
from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages.template import (
    VKMessageText,
    build_template_message,
)


def build_store_root_message(*, balance_points: int) -> VKMessageText:
    return VKMessageText(
        text=(
            "🎁 Магазин призов\n\n"
            f"Баланс: {balance_points} ✦\n\n"
            "Выбери раздел каталога или открой «Мои призы»."
        ),
    )


def build_store_catalog_message(*, catalog: StoreCatalogDTO) -> VKMessageText:
    header = (
        f"🎁 Магазин · {catalog.section.label}\n\n"
        f"Баланс: {catalog.balance_points} ✦\n"
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
    return build_template_message(
        "store_catalog_navigation",
        section_label=catalog.section.label,
        page=catalog.pagination.page,
        total_pages=catalog.pagination.total_pages,
    )


def build_store_catalog_carousel_message(*, catalog: StoreCatalogDTO) -> VKMessageText:
    return build_template_message(
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


def build_store_claim_confirm_message(*, card: StorePrizeCardDTO) -> VKMessageText:
    prize = card.prize
    if prize is None:
        return build_store_prize_not_found_message()

    balance_after = card.balance_points - prize.cost_points
    result_text = (
        "Промокод будет отправлен сразу после покупки."
        if prize.prize_type == PrizeType.PARTNER
        else "Заявка на самовывоз будет создана сразу."
    )
    return VKMessageText(
        text=(
            f"🎁 {prize.prize_name}\n\n"
            f"Списать {prize.cost_points} ✦?\n"
            f"Баланс после покупки: {balance_after} ✦\n"
            f"Остаток приза: {prize.quantity_remaining} из {prize.quantity_total}\n\n"
            f"Подтверди покупку — {result_text}"
        ),
    )


def build_store_redeem_outcome_message(
    *,
    outcome: RedeemPrizeOutcome,
    balance_points: int,
) -> VKMessageText:
    if outcome.status in (
        RedeemPrizeOutcomeStatus.COMPLETED,
        RedeemPrizeOutcomeStatus.IDEMPOTENT_REPLAY,
    ):
        if outcome.promo_code:
            return VKMessageText(
                text=(
                    f"🎁 {outcome.prize_name or 'Приз'}\n\n"
                    f"Промокод: {outcome.promo_code}\n"
                    f"Списано: {outcome.points_spent} ✦\n"
                    f"Баланс: {outcome.balance_points if outcome.balance_points is not None else balance_points} ✦\n\n"
                    "Промокод сохранён в разделе «Мои призы»."
                ),
            )
        return build_template_message(
            "store_pickup_success",
            prize_name=outcome.prize_name or "Приз",
            redemption_code=outcome.redemption_code or "",
            points_spent=outcome.points_spent,
            balance_points=outcome.balance_points if outcome.balance_points is not None else balance_points,
        )

    if outcome.status == RedeemPrizeOutcomeStatus.SOLD_OUT:
        return VKMessageText(text="🔴 Этот приз уже разобрали. Попробуй другой из каталога.")
    if outcome.status == RedeemPrizeOutcomeStatus.INSUFFICIENT_BALANCE:
        return VKMessageText(text=f"Не хватает баллов. Баланс: {balance_points} ✦")
    if outcome.status == RedeemPrizeOutcomeStatus.LEVEL_LOCKED:
        return VKMessageText(text="🔒 Приз доступен с более высоким уровнем участника.")
    if outcome.status == RedeemPrizeOutcomeStatus.IDEMPOTENCY_CONFLICT:
        return VKMessageText(text="Не удалось подтвердить покупку. Открой приз в магазине и попробуй снова.")
    if outcome.status == RedeemPrizeOutcomeStatus.PRIZE_NOT_FOUND:
        return build_store_prize_not_found_message()
    return VKMessageText(text="Приз сейчас недоступен для покупки.")


def build_store_my_redemptions_message(*, listing: ListUserRedemptionsDTO) -> VKMessageText:
    if not listing.redemptions:
        return VKMessageText(
            text="📦 Мои призы\n\nУ тебя пока нет заявок. Выбери приз в магазине и оформи самовывоз.",
        )

    lines = ["📦 Мои призы", ""]
    for item in listing.redemptions:
        code_label = "Промокод" if item.promo_code else "Код"
        code_value = item.promo_code or item.redemption_code
        lines.append(
            f"• {item.prize_name} — {_format_redemption_status(item.prize_redemption_status)}\n"
            f"  {code_label}: {code_value}",
        )
    return VKMessageText(text="\n".join(lines))


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
    return f"{prize.quantity_remaining} из {prize.quantity_total}"


def _format_redemption_status(status: PrizeRedemptionStatus) -> str:
    if status == PrizeRedemptionStatus.RESERVED:
        return "ожидает выдачи"
    if status == PrizeRedemptionStatus.ISSUED:
        return "выдан"
    return "отменён"


def _format_prize_type(prize_type: PrizeType) -> str:
    if prize_type == PrizeType.MERCH:
        return "Мерч"
    if prize_type == PrizeType.PARTNER:
        return "Твой подарок"
    if prize_type == PrizeType.SUPER_PRIZE:
        return "Суперприз"
    return "Приз"


def _format_optional_description(description: str | None) -> str:
    clean_description = description.strip() if description is not None else ""
    if not clean_description:
        return ""
    return f"\n\n{clean_description}"
