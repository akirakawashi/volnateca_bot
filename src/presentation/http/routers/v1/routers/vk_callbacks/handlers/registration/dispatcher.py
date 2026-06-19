"""Маршрутизация payload-action-ов зарегистрированного пользователя в обработчики."""

from application.command.answer_quiz_question import AnswerQuizQuestionHandler
from application.command.get_quiz_first_question import GetQuizFirstQuestionHandler
from application.command.get_store_catalog import GetStoreCatalogHandler, GetStorePrizeCardHandler
from application.command.list_user_redemptions import ListUserRedemptionsHandler
from application.command.redeem_prize import RedeemPrizeHandler
from application.command.get_vk_user_tasks import GetVKUserTasksHandler
from application.command.task_promo_code import (
    ActivateTaskPromoCodeHandler,
    CancelTaskPromoCodeHandler,
    GetTaskPromoCodeWaitCommand,
    GetTaskPromoCodeWaitHandler,
    StartTaskPromoCodeHandler,
    TaskPromoCodeFlowStatus,
)
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionDTO,
)
from application.interface.clients import IVKMessageClient
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.actions import (
    BALANCE_ACTION,
    BOT_SUPPORT_ACTION,
    CUSTOM_PROMO_EXIT_ACTION,
    CUSTOM_PROMO_START_ACTION,
    REFERRAL_ACTION,
    SHOP_ACTION,
    SUPPORT_ACTION,
    TASKS_ACTION,
    TASKS_PAGE_ACTION,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.balance import handle_balance
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.bot_support import handle_bot_support
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.payload_parsing import (
    parse_payload_str,
    parse_positive_int,
    parse_store_page,
    parse_store_section,
    parse_tasks_page,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.quiz import (
    handle_quiz_answer,
    handle_skip_quiz,
    handle_start_quiz,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.referral import handle_referral
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.support import handle_support
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.store import (
    handle_store_catalog,
    handle_store_claim,
    handle_store_claim_confirm,
    handle_store_exit,
    handle_store_my_redemptions,
    handle_store_prize_card,
    handle_store_root,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.tasks import (
    handle_task_info,
    handle_tasks,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.task_promo_code import (
    handle_task_promo_code_exit,
    handle_task_promo_code_start,
    handle_task_promo_code_text,
)
from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload
from settings.vk.task_images import TaskTypeImagesSettings


async def handle_registered_user_message(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
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
    group_id: int,
    task_images_settings: TaskTypeImagesSettings,
    support_link: str,
    bot_support_link: str,
) -> bool:
    """Обрабатывает только payload-кнопки зарегистрированного пользователя."""

    button_payload = data.get_button_payload()
    action = button_payload.get("action") if button_payload is not None else None

    if button_payload is None:
        return await handle_task_promo_code_text(
            data=data,
            result=result,
            message_client=message_client,
            activate_task_promo_code_interactor=activate_task_promo_code_interactor,
        )

    if action == CUSTOM_PROMO_EXIT_ACTION:
        await handle_task_promo_code_exit(
            data=data,
            result=result,
            message_client=message_client,
            cancel_task_promo_code_interactor=cancel_task_promo_code_interactor,
        )
        return True

    wait = await get_task_promo_code_wait_interactor(
        command_data=GetTaskPromoCodeWaitCommand(vk_user_id=result.registration.vk_user_id),
    )
    if wait.status == TaskPromoCodeFlowStatus.STARTED:
        return True

    if button_payload is not None:
        if action == BALANCE_ACTION:
            await handle_balance(
                data=data,
                result=result,
                message_client=message_client,
            )
            return True
        if action == TASKS_ACTION:
            await handle_tasks(
                data=data,
                result=result,
                page=parse_tasks_page(button_payload.get("page")),
                include_quiz_offer=True,
                message_client=message_client,
                get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
                task_images_settings=task_images_settings,
            )
            return True
        if action == TASKS_PAGE_ACTION:
            await handle_tasks(
                data=data,
                result=result,
                page=parse_tasks_page(button_payload.get("page")),
                include_quiz_offer=False,
                message_client=message_client,
                get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
                task_images_settings=task_images_settings,
            )
            return True
        if action == SHOP_ACTION:
            await handle_store_root(
                data=data,
                result=result,
                message_client=message_client,
            )
            return True
        if action == REFERRAL_ACTION:
            await handle_referral(
                data=data,
                result=result,
                group_id=group_id,
                message_client=message_client,
            )
            return True
        if action == SUPPORT_ACTION:
            await handle_support(
                data=data,
                result=result,
                message_client=message_client,
                support_link=support_link,
            )
            return True
        if action == BOT_SUPPORT_ACTION:
            await handle_bot_support(
                data=data,
                result=result,
                message_client=message_client,
                bot_support_link=bot_support_link,
            )
            return True
        if action == CUSTOM_PROMO_START_ACTION:
            tasks_id = parse_positive_int(button_payload.get("tasks_id"))
            if tasks_id is not None:
                await handle_task_promo_code_start(
                    data=data,
                    result=result,
                    tasks_id=tasks_id,
                    message_client=message_client,
                    start_task_promo_code_interactor=start_task_promo_code_interactor,
                )
                return True
        if action == "store_root":
            await handle_store_root(
                data=data,
                result=result,
                message_client=message_client,
            )
            return True
        if action == "store_exit":
            await handle_store_exit(
                data=data,
                result=result,
                message_client=message_client,
            )
            return True
        if action == "store_catalog":
            await handle_store_catalog(
                data=data,
                result=result,
                section=parse_store_section(button_payload.get("section")),
                page=parse_store_page(button_payload.get("page")),
                message_client=message_client,
                get_store_catalog_interactor=get_store_catalog_interactor,
            )
            return True
        if action == "store_prize":
            prizes_id = parse_positive_int(button_payload.get("prizes_id"))
            if prizes_id is None:
                await handle_store_root(
                    data=data,
                    result=result,
                    message_client=message_client,
                )
                return True
            await handle_store_prize_card(
                data=data,
                result=result,
                prizes_id=prizes_id,
                section=parse_store_section(button_payload.get("section")),
                page=parse_store_page(button_payload.get("page")),
                message_client=message_client,
                get_store_prize_card_interactor=get_store_prize_card_interactor,
            )
            return True
        if action == "store_claim":
            prizes_id = parse_positive_int(button_payload.get("prizes_id"))
            await handle_store_claim(
                data=data,
                result=result,
                prizes_id=prizes_id,
                section=parse_store_section(button_payload.get("section")),
                page=parse_store_page(button_payload.get("page")),
                message_client=message_client,
                get_store_prize_card_interactor=get_store_prize_card_interactor,
            )
            return True
        if action == "store_claim_confirm":
            prizes_id = parse_positive_int(button_payload.get("prizes_id"))
            await handle_store_claim_confirm(
                data=data,
                result=result,
                prizes_id=prizes_id,
                section=parse_store_section(button_payload.get("section")),
                page=parse_store_page(button_payload.get("page")),
                idempotency_key=parse_payload_str(button_payload.get("idempotency_key")),
                message_client=message_client,
                get_store_prize_card_interactor=get_store_prize_card_interactor,
                redeem_prize_interactor=redeem_prize_interactor,
            )
            return True
        if action == "store_my_redemptions":
            await handle_store_my_redemptions(
                data=data,
                result=result,
                page=parse_store_page(button_payload.get("page")),
                message_client=message_client,
                list_user_redemptions_interactor=list_user_redemptions_interactor,
            )
            return True
        if action == "start_quiz":
            tasks_id = button_payload.get("tasks_id")
            if isinstance(tasks_id, int):
                await handle_start_quiz(
                    data=data,
                    result=result,
                    tasks_id=tasks_id,
                    message_client=message_client,
                    get_quiz_first_question_interactor=get_quiz_first_question_interactor,
                    get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
                    task_images_settings=task_images_settings,
                )
                return True
        elif action == "skip_quiz":
            await handle_skip_quiz(
                data=data,
                result=result,
                message_client=message_client,
                get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
                task_images_settings=task_images_settings,
            )
            return True
        elif action == "quiz_answer":
            quiz_questions_id = button_payload.get("quiz_questions_id")
            option_id = button_payload.get("option_id")
            if isinstance(quiz_questions_id, int) and isinstance(option_id, int):
                await handle_quiz_answer(
                    data=data,
                    result=result,
                    quiz_questions_id=quiz_questions_id,
                    quiz_question_options_id=option_id,
                    message_client=message_client,
                    answer_quiz_question_interactor=answer_quiz_question_interactor,
                )
                return True
        elif action == "task_info":
            tasks_id = button_payload.get("tasks_id")
            if isinstance(tasks_id, int):
                await handle_task_info(
                    data=data,
                    result=result,
                    tasks_id=tasks_id,
                    page=parse_tasks_page(button_payload.get("page")),
                    message_client=message_client,
                    get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
                )
                return True

    return False
