"""Маршрутизация payload-action-ов зарегистрированного пользователя в обработчики."""

from application.command.answer_quiz_question import AnswerQuizQuestionHandler
from application.command.get_quiz_first_question import GetQuizFirstQuestionHandler
from application.command.get_store_catalog import GetStoreCatalogHandler, GetStorePrizeCardHandler
from application.command.get_vk_user_tasks import GetVKUserTasksHandler
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionDTO,
)
from application.interface.clients import IVKMessageClient
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.actions import (
    BALANCE_ACTION,
    REFERRAL_ACTION,
    SHOP_ACTION,
    TASKS_ACTION,
    TASKS_PAGE_ACTION,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.balance import handle_balance
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.payload_parsing import (
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
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.store import (
    handle_store_catalog,
    handle_store_claim,
    handle_store_exit,
    handle_store_prize_card,
    handle_store_root,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.tasks import (
    handle_task_info,
    handle_tasks,
)
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from settings.vk.task_images import TaskTypeImagesSettings


async def handle_registered_user_message(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
    get_vk_user_tasks_interactor: GetVKUserTasksHandler,
    get_store_catalog_interactor: GetStoreCatalogHandler,
    get_store_prize_card_interactor: GetStorePrizeCardHandler,
    get_quiz_first_question_interactor: GetQuizFirstQuestionHandler,
    answer_quiz_question_interactor: AnswerQuizQuestionHandler,
    group_id: int,
    task_images_settings: TaskTypeImagesSettings,
) -> None:
    """Обрабатывает только payload-кнопки зарегистрированного пользователя."""

    button_payload = data.get_button_payload()
    if button_payload is not None:
        action = button_payload.get("action")
        if action == BALANCE_ACTION:
            await handle_balance(
                data=data,
                result=result,
                message_client=message_client,
            )
            return
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
            return
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
            return
        if action == SHOP_ACTION:
            await handle_store_root(
                data=data,
                result=result,
                message_client=message_client,
            )
            return
        if action == REFERRAL_ACTION:
            await handle_referral(
                data=data,
                result=result,
                group_id=group_id,
                message_client=message_client,
            )
            return
        if action == "store_root":
            await handle_store_root(
                data=data,
                result=result,
                message_client=message_client,
            )
            return
        if action == "store_exit":
            await handle_store_exit(
                data=data,
                result=result,
                message_client=message_client,
            )
            return
        if action == "store_catalog":
            await handle_store_catalog(
                data=data,
                result=result,
                section=parse_store_section(button_payload.get("section")),
                page=parse_store_page(button_payload.get("page")),
                message_client=message_client,
                get_store_catalog_interactor=get_store_catalog_interactor,
            )
            return
        if action == "store_prize":
            prizes_id = parse_positive_int(button_payload.get("prizes_id"))
            if prizes_id is None:
                await handle_store_root(
                    data=data,
                    result=result,
                    message_client=message_client,
                )
                return
            await handle_store_prize_card(
                data=data,
                result=result,
                prizes_id=prizes_id,
                section=parse_store_section(button_payload.get("section")),
                page=parse_store_page(button_payload.get("page")),
                message_client=message_client,
                get_store_prize_card_interactor=get_store_prize_card_interactor,
            )
            return
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
            return
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
                return
        elif action == "skip_quiz":
            await handle_skip_quiz(
                data=data,
                result=result,
                message_client=message_client,
                get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
                task_images_settings=task_images_settings,
            )
            return
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
                return
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
                return

    return
