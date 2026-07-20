"""Точка входа в registration-флоу (VK-события MESSAGE_NEW + MESSAGE_ALLOW).

Содержит публичную функцию ``handle_registration_callback``, а также узко
связанные с ней send-хелперы регистрационного пути (consent, welcome, награда
за подписку при регистрации, главное меню).
"""

from fastapi.responses import PlainTextResponse

from application.command.answer_quiz_question import AnswerQuizQuestionHandler
from application.command.capture_vk_referral_intent import (
    CaptureVKReferralIntentCommand,
    CaptureVKReferralIntentHandler,
)
from application.command.get_quiz_first_question import GetQuizFirstQuestionHandler
from application.command.get_store_catalog import GetStoreCatalogHandler, GetStorePrizeCardHandler
from application.command.list_user_redemptions import ListUserRedemptionsHandler
from application.command.redeem_prize import RedeemPrizeHandler
from application.command.get_vk_user_tasks import GetVKUserTasksHandler
from application.command.register_vk_user import REGISTRATION_BONUS_POINTS
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionDTO,
)
from application.command.register_vk_user_with_referral_context import (
    RegisterVKUserWithReferralContextCommand,
    RegisterVKUserWithReferralContextHandler,
)
from application.command.task_promo_code import (
    ActivateTaskPromoCodeHandler,
    CancelTaskPromoCodeHandler,
    GetTaskPromoCodeWaitHandler,
    StartTaskPromoCodeHandler,
)
from application.common.dto.task import TaskCompletionResultStatus
from application.interface.clients import IVKMessageClient
from application.interface.repositories.users import IUserRepository
from presentation.http.routers.v1.routers.vk_callbacks.handlers.achievement import (
    send_project_completion_reward_if_needed,
    send_week_completion_reward_if_needed,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.actions import (
    CONSENT_ACCEPT_ACTION,
    CONSENT_DECLINE_ACTION,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.dispatcher import (
    handle_registered_user_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.payload_parsing import (
    extract_consent_ref_key,
    is_default_start_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.referral import (
    send_referral_notifications,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards import build_consent_keyboard
from presentation.http.routers.v1.routers.vk_callbacks.outbound.sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages import (
    build_consent_request_message,
    build_game_entry_help_message,
    build_main_menu_message,
    build_registration_welcome_message,
    build_subscription_reward_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.protocol.responses import vk_ok_response
from settings.vk.task_images import TaskTypeImagesSettings


async def handle_registration_callback(
    data: VKCallbackPayload,
    register_with_referral_context_interactor: RegisterVKUserWithReferralContextHandler,
    get_vk_user_tasks_interactor: GetVKUserTasksHandler,
    get_store_catalog_interactor: GetStoreCatalogHandler,
    get_store_prize_card_interactor: GetStorePrizeCardHandler,
    redeem_prize_interactor: RedeemPrizeHandler,
    list_user_redemptions_interactor: ListUserRedemptionsHandler,
    get_quiz_first_question_interactor: GetQuizFirstQuestionHandler,
    answer_quiz_question_interactor: AnswerQuizQuestionHandler,
    start_task_promo_code_interactor: StartTaskPromoCodeHandler,
    activate_task_promo_code_interactor: ActivateTaskPromoCodeHandler,
    cancel_task_promo_code_interactor: CancelTaskPromoCodeHandler,
    get_task_promo_code_wait_interactor: GetTaskPromoCodeWaitHandler,
    capture_referral_intent_interactor: CaptureVKReferralIntentHandler,
    group_id: int,
    task_images_settings: TaskTypeImagesSettings,
    message_client: IVKMessageClient,
    user_repository: IUserRepository,
    support_link: str,
    bot_support_link: str,
) -> PlainTextResponse:
    """Обрабатывает первый контакт пользователя и обычные сообщения в бота.

    Игра реагирует на payload-кнопки и стартовые команды.
    Остальной свободный текст получает подсказку с поддержкой и командой входа.

    Уже зарегистрированного пользователя обрабатывает только для message_new,
    чтобы callback-и подписки/разрешения сообщений не дублировали ответы.
    """

    vk_user_id = data.get_vk_user_id()
    if vk_user_id is None:
        return vk_ok_response()

    button_payload = data.get_button_payload()
    action = button_payload.get("action") if button_payload is not None else None

    if action is None:
        existing_user = None
        existing_user_loaded = False
        raw_ref = data.get_ref_key()
        if raw_ref is not None:
            existing_user = await user_repository.get_by_vk_user_id(vk_user_id=vk_user_id)
            existing_user_loaded = True
            if existing_user is None:
                await capture_referral_intent_interactor(
                    command_data=CaptureVKReferralIntentCommand(
                        invited_vk_user_id=vk_user_id,
                        raw_ref=raw_ref,
                    ),
                )

        if not existing_user_loaded:
            existing_user = await user_repository.get_by_vk_user_id(vk_user_id=vk_user_id)
        if existing_user is not None:
            result = RegisterVKUserAndCheckSubscriptionDTO(
                registration=existing_user,
                subscription=None,
            )
            if data.is_message_new():
                handled = await handle_registered_user_message(
                    data=data,
                    result=result,
                    message_client=message_client,
                    get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
                    get_store_catalog_interactor=get_store_catalog_interactor,
                    get_store_prize_card_interactor=get_store_prize_card_interactor,
                    redeem_prize_interactor=redeem_prize_interactor,
                    list_user_redemptions_interactor=list_user_redemptions_interactor,
                    get_quiz_first_question_interactor=get_quiz_first_question_interactor,
                    answer_quiz_question_interactor=answer_quiz_question_interactor,
                    start_task_promo_code_interactor=start_task_promo_code_interactor,
                    activate_task_promo_code_interactor=activate_task_promo_code_interactor,
                    cancel_task_promo_code_interactor=cancel_task_promo_code_interactor,
                    get_task_promo_code_wait_interactor=get_task_promo_code_wait_interactor,
                    group_id=group_id,
                    task_images_settings=task_images_settings,
                    support_link=support_link,
                    bot_support_link=bot_support_link,
                )
                if handled:
                    return vk_ok_response()
            if not data.is_message_new():
                return vk_ok_response()
            if not is_default_start_message(data):
                await _send_game_entry_help_message(
                    data=data,
                    vk_user_id=result.registration.vk_user_id,
                    users_id=result.registration.users_id,
                    support_link=support_link,
                    message_client=message_client,
                )
                return vk_ok_response()

            await _send_main_menu_message(
                data=data,
                result=result,
                message_client=message_client,
            )
            return vk_ok_response()

        if not data.is_message_new():
            return vk_ok_response()
        if not is_default_start_message(data):
            await _send_game_entry_help_message(
                data=data,
                vk_user_id=vk_user_id,
                users_id=None,
                support_link=support_link,
                message_client=message_client,
            )
            return vk_ok_response()

        await _send_consent_request_message(
            data=data,
            vk_user_id=vk_user_id,
            message_client=message_client,
            ref_key=raw_ref,
        )
        return vk_ok_response()

    existing_user = await user_repository.get_by_vk_user_id(vk_user_id=vk_user_id)
    if existing_user is not None:
        if action == CONSENT_ACCEPT_ACTION:
            registration_context = await register_with_referral_context_interactor(
                command_data=RegisterVKUserWithReferralContextCommand(
                    event_id=data.event_id,
                    vk_user_id=vk_user_id,
                    first_name=data.get_first_name(),
                    last_name=data.get_last_name(),
                    retry_referral_for_existing_user=True,
                ),
            )
            await send_referral_notifications(
                data=data,
                referral_result=registration_context.referral_result,
                message_client=message_client,
            )
            return vk_ok_response()
        if action == CONSENT_DECLINE_ACTION:
            return vk_ok_response()
        result = RegisterVKUserAndCheckSubscriptionDTO(
            registration=existing_user,
            subscription=None,
        )
        if data.is_message_new():
            await handle_registered_user_message(
                data=data,
                result=result,
                message_client=message_client,
                get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
                get_store_catalog_interactor=get_store_catalog_interactor,
                get_store_prize_card_interactor=get_store_prize_card_interactor,
                redeem_prize_interactor=redeem_prize_interactor,
                list_user_redemptions_interactor=list_user_redemptions_interactor,
                get_quiz_first_question_interactor=get_quiz_first_question_interactor,
                answer_quiz_question_interactor=answer_quiz_question_interactor,
                start_task_promo_code_interactor=start_task_promo_code_interactor,
                activate_task_promo_code_interactor=activate_task_promo_code_interactor,
                cancel_task_promo_code_interactor=cancel_task_promo_code_interactor,
                get_task_promo_code_wait_interactor=get_task_promo_code_wait_interactor,
                group_id=group_id,
                task_images_settings=task_images_settings,
                support_link=support_link,
                bot_support_link=bot_support_link,
            )
        return vk_ok_response()

    if action == CONSENT_DECLINE_ACTION:
        return vk_ok_response()
    if action != CONSENT_ACCEPT_ACTION:
        return vk_ok_response()

    registration_context = await register_with_referral_context_interactor(
        command_data=RegisterVKUserWithReferralContextCommand(
            event_id=data.event_id,
            vk_user_id=vk_user_id,
            first_name=data.get_first_name(),
            last_name=data.get_last_name(),
            raw_ref=extract_consent_ref_key(button_payload=button_payload, data=data),
        ),
    )
    registration_result = registration_context.registration_result
    if registration_result.registration.created:
        await _send_registration_welcome_message(
            data=data,
            result=registration_result,
            message_client=message_client,
        )
        await _send_subscription_reward_message_after_registration(
            data=data,
            result=registration_result,
            message_client=message_client,
        )
        await send_referral_notifications(
            data=data,
            referral_result=registration_context.referral_result,
            message_client=message_client,
        )
    return vk_ok_response()


async def _send_consent_request_message(
    *,
    data: VKCallbackPayload,
    vk_user_id: int,
    message_client: IVKMessageClient,
    ref_key: str | None,
) -> None:
    await send_vk_user_message(
        data=data,
        vk_user_id=vk_user_id,
        users_id=None,
        message=build_consent_request_message(),
        keyboard=build_consent_keyboard(ref_key=ref_key),
        dont_parse_links=True,
        message_client=message_client,
        log_message="Сообщение с запросом согласия VK",
    )


async def _send_game_entry_help_message(
    *,
    data: VKCallbackPayload,
    vk_user_id: int,
    users_id: int | None,
    support_link: str,
    message_client: IVKMessageClient,
) -> None:
    await send_vk_user_message(
        data=data,
        vk_user_id=vk_user_id,
        users_id=users_id,
        message=build_game_entry_help_message(support_link=support_link),
        message_client=message_client,
        log_message="Подсказка входа в игру VK",
    )


async def _send_main_menu_message(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
) -> None:
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_main_menu_message(),
        message_client=message_client,
        log_message="Главное меню VK",
    )


async def _send_registration_welcome_message(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
) -> None:
    message = build_registration_welcome_message(
        first_name=data.get_first_name(),
        balance_points=result.registration.balance_points,
        bonus_points=REGISTRATION_BONUS_POINTS,
    )
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=message,
        message_client=message_client,
        log_message="Приветственное сообщение VK после регистрации",
    )


async def _send_subscription_reward_message_after_registration(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
) -> None:
    subscription = result.subscription
    if subscription is None or subscription.status != TaskCompletionResultStatus.COMPLETED:
        return
    if subscription.balance_points is None:
        return

    message = build_subscription_reward_message(
        points_awarded=subscription.points_awarded,
        balance_points=subscription.balance_points,
    )
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=message,
        message_client=message_client,
        log_message="Сообщение о награде за подписку VK после регистрации",
    )
    await send_week_completion_reward_if_needed(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        week_number=subscription.week_completion_week_number,
        points_awarded=subscription.week_completion_points_awarded,
        balance_points=subscription.week_completion_balance_points,
        level_up=subscription.week_completion_level_up,
        message_client=message_client,
    )
    await send_project_completion_reward_if_needed(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        points_awarded=subscription.project_completion_points_awarded,
        balance_points=subscription.project_completion_balance_points,
        level_up=subscription.project_completion_level_up,
        message_client=message_client,
    )
