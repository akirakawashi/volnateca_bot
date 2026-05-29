"""Обработчики экранов магазина: корень, каталог, карточки призов, покупка, выход."""

import uuid

from application.command.get_store_catalog import (
    GetStoreCatalogCommand,
    GetStoreCatalogHandler,
    GetStorePrizeCardCommand,
    GetStorePrizeCardHandler,
)
from application.command.list_user_redemptions import (
    ListUserRedemptionsCommand,
    ListUserRedemptionsHandler,
)
from application.command.redeem_prize import RedeemPrizeCommand, RedeemPrizeHandler
from application.common.dto.store import StorePrizeUserState
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionDTO,
)
from application.common.dto.store import StoreSection
from application.interface.clients import IVKMessageClient
from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards import (
    build_store_catalog_carousel_template,
    build_store_catalog_keyboard,
    build_store_catalog_navigation_keyboard,
    build_store_claim_confirm_keyboard,
    build_store_exit_keyboard,
    build_store_my_redemptions_keyboard,
    build_store_prize_card_keyboard,
    build_store_prize_not_found_keyboard,
    build_store_redeem_result_keyboard,
    build_store_root_keyboard,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages import (
    build_store_catalog_carousel_message,
    build_store_catalog_message,
    build_store_catalog_navigation_message,
    build_store_claim_confirm_message,
    build_store_exit_message,
    build_store_my_redemptions_message,
    build_store_prize_card_message,
    build_store_redeem_outcome_message,
    build_store_root_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload
from utils.vk_attachments import normalize_vk_photo_attachment


async def handle_store_root(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
) -> None:
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_store_root_message(balance_points=result.registration.balance_points),
        keyboard=build_store_root_keyboard(),
        message_client=message_client,
        log_message="Корневой экран магазина VK",
    )


async def handle_store_exit(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
) -> None:
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_store_exit_message(),
        keyboard=build_store_exit_keyboard(),
        message_client=message_client,
        log_message="Выход из магазина VK",
    )


async def handle_store_catalog(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    section: StoreSection,
    page: int,
    message_client: IVKMessageClient,
    get_store_catalog_interactor: GetStoreCatalogHandler,
) -> None:
    catalog = await get_store_catalog_interactor(
        command_data=GetStoreCatalogCommand(
            balance_points=result.registration.balance_points,
            current_level=result.registration.current_level,
            section=section,
            page=page,
        ),
    )
    carousel_template = build_store_catalog_carousel_template(catalog)
    if carousel_template is not None:
        await send_vk_user_message(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            message=build_store_catalog_navigation_message(catalog=catalog),
            keyboard=build_store_catalog_navigation_keyboard(catalog),
            message_client=message_client,
            log_message="Навигация каталога магазина VK",
        )
        sent = await send_vk_user_message(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            message=build_store_catalog_carousel_message(catalog=catalog),
            keyboard=None,
            template=carousel_template,
            message_client=message_client,
            log_message="Карусель каталога магазина VK",
        )
        if sent:
            return

    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_store_catalog_message(catalog=catalog),
        keyboard=build_store_catalog_keyboard(catalog, include_prize_buttons=True),
        message_client=message_client,
        log_message="Каталог магазина VK без карусели",
    )


async def handle_store_prize_card(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    prizes_id: int,
    section: StoreSection,
    page: int,
    message_client: IVKMessageClient,
    get_store_prize_card_interactor: GetStorePrizeCardHandler,
) -> None:
    card = await get_store_prize_card_interactor(
        command_data=GetStorePrizeCardCommand(
            prizes_id=prizes_id,
            balance_points=result.registration.balance_points,
            current_level=result.registration.current_level,
            section=section,
            page=page,
        ),
    )
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_store_prize_card_message(card=card),
        keyboard=(
            build_store_prize_card_keyboard(card)
            if card.prize is not None
            else build_store_prize_not_found_keyboard()
        ),
        message_client=message_client,
        log_message="Карточка приза VK",
        attachment=normalize_vk_photo_attachment(card.prize.image_attachment) if card.prize is not None else None,
    )


async def handle_store_claim(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    prizes_id: int | None,
    section: StoreSection,
    page: int,
    message_client: IVKMessageClient,
    get_store_prize_card_interactor: GetStorePrizeCardHandler,
) -> None:
    if prizes_id is None or result.registration.users_id is None:
        await handle_store_root(
            data=data,
            result=result,
            message_client=message_client,
        )
        return

    card = await get_store_prize_card_interactor(
        command_data=GetStorePrizeCardCommand(
            prizes_id=prizes_id,
            balance_points=result.registration.balance_points,
            current_level=result.registration.current_level,
            section=section,
            page=page,
        ),
    )
    if card.prize is None or card.prize.user_state != StorePrizeUserState.AVAILABLE:
        await handle_store_prize_card(
            data=data,
            result=result,
            prizes_id=prizes_id,
            section=section,
            page=page,
            message_client=message_client,
            get_store_prize_card_interactor=get_store_prize_card_interactor,
        )
        return

    idempotency_key = str(uuid.uuid4())
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_store_claim_confirm_message(card=card),
        keyboard=build_store_claim_confirm_keyboard(
            prizes_id=prizes_id,
            section=section.value,
            page=page,
            idempotency_key=idempotency_key,
        ),
        message_client=message_client,
        log_message="Подтверждение покупки приза VK",
        attachment=normalize_vk_photo_attachment(card.prize.image_attachment),
    )


async def handle_store_claim_confirm(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    prizes_id: int | None,
    section: StoreSection,
    page: int,
    idempotency_key: str | None,
    message_client: IVKMessageClient,
    get_store_prize_card_interactor: GetStorePrizeCardHandler,
    redeem_prize_interactor: RedeemPrizeHandler,
) -> None:
    if (
        prizes_id is None
        or result.registration.users_id is None
        or idempotency_key is None
    ):
        await handle_store_root(
            data=data,
            result=result,
            message_client=message_client,
        )
        return

    outcome = await redeem_prize_interactor(
        command_data=RedeemPrizeCommand(
            vk_user_id=result.registration.vk_user_id,
            prizes_id=prizes_id,
            idempotency_key=idempotency_key,
        ),
    )
    balance_points = (
        outcome.balance_points
        if outcome.balance_points is not None
        else result.registration.balance_points
    )

    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_store_redeem_outcome_message(
            outcome=outcome,
            balance_points=balance_points,
        ),
        keyboard=build_store_redeem_result_keyboard(section=section.value, page=page),
        message_client=message_client,
        log_message="Покупка приза VK",
    )


async def handle_store_my_redemptions(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    page: int,
    message_client: IVKMessageClient,
    list_user_redemptions_interactor: ListUserRedemptionsHandler,
) -> None:
    if result.registration.users_id is None:
        await handle_store_root(
            data=data,
            result=result,
            message_client=message_client,
        )
        return

    listing = await list_user_redemptions_interactor(
        command_data=ListUserRedemptionsCommand(
            users_id=result.registration.users_id,
            page=page,
        ),
    )
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_store_my_redemptions_message(listing=listing),
        keyboard=build_store_my_redemptions_keyboard(
            page=listing.page,
            has_previous=listing.has_previous,
            has_next=listing.has_next,
        ),
        message_client=message_client,
        log_message="Список заявок на призы VK",
    )
