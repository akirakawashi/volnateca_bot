from fastapi.responses import PlainTextResponse

from application.command.answer_quiz_question import (
    AnswerQuizQuestionCommand,
    AnswerQuizQuestionHandler,
)
from application.command.get_quiz_first_question import (
    GetQuizFirstQuestionCommand,
    GetQuizFirstQuestionHandler,
)
from application.command.get_vk_user_tasks import GetVKUserTasksCommand, GetVKUserTasksHandler
from application.command.process_referral import ProcessReferralCommand, ProcessReferralHandler
from application.command.register_vk_user import REGISTRATION_BONUS_POINTS
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionCommand,
    RegisterVKUserAndCheckSubscriptionDTO,
    RegisterVKUserAndCheckSubscriptionHandler,
)
from application.common.dto.task import TaskCompletionResultStatus
from application.common.dto.user_message import UserMessageIntent
from application.interface.clients import IVKMessageClient
from application.interface.services import IUserMessageIntentClassifier
from domain.services.level import get_level_name
from presentation.http.routers.v1.routers.vk_callbacks.handlers.achievement import (
    send_quiz_streak_reward_if_needed,
    send_week_completion_reward_if_needed,
)
from presentation.http.routers.v1.routers.vk_callbacks.keyboards import (
    build_quiz_offer_keyboard,
    build_quiz_question_keyboard,
)
from presentation.http.routers.v1.routers.vk_callbacks.messages import (
    VKMessageText,
    build_balance_message,
    build_free_text_fallback_message,
    build_help_message,
    build_level_up_message,
    build_quiz_answer_result_message,
    build_quiz_completed_message,
    build_quiz_offer_message,
    build_quiz_question_message,
    build_quiz_unavailable_message,
    build_referral_bonus_message,
    build_referral_link_message,
    build_referral_milestone_message,
    build_registration_welcome_message,
    build_subscription_reward_message,
    build_tasks_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.message_sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_registration_callback(
    data: VKCallbackPayload,
    interactor: RegisterVKUserAndCheckSubscriptionHandler,
    get_vk_user_tasks_interactor: GetVKUserTasksHandler,
    get_quiz_first_question_interactor: GetQuizFirstQuestionHandler,
    answer_quiz_question_interactor: AnswerQuizQuestionHandler,
    process_referral_interactor: ProcessReferralHandler,
    group_id: int,
    message_client: IVKMessageClient,
    intent_classifier: IUserMessageIntentClassifier,
) -> PlainTextResponse:
    """Обрабатывает первый контакт пользователя и обычные сообщения в бота.

    Нового пользователя регистрирует и запускает приветственные сценарии.
    Уже зарегистрированного пользователя обрабатывает только для message_new,
    чтобы callback-и подписки/разрешения сообщений не дублировали ответы.
    """

    vk_user_id = data.get_vk_user_id()
    if vk_user_id is None:
        return vk_ok_response()

    result = await interactor(
        command_data=RegisterVKUserAndCheckSubscriptionCommand(
            event_id=data.event_id,
            vk_user_id=vk_user_id,
            first_name=data.get_first_name(),
            last_name=data.get_last_name(),
        ),
    )
    if result.registration.created:
        await _send_registration_welcome_message(
            data=data,
            result=result,
            message_client=message_client,
        )
        await _send_subscription_reward_message_after_registration(
            data=data,
            result=result,
            message_client=message_client,
        )
        await _process_referral_on_registration(
            data=data,
            result=result,
            process_referral_interactor=process_referral_interactor,
            message_client=message_client,
        )
    elif data.is_message_new():
        await _handle_registered_user_message(
            data=data,
            result=result,
            message_client=message_client,
            intent_classifier=intent_classifier,
            get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
            get_quiz_first_question_interactor=get_quiz_first_question_interactor,
            answer_quiz_question_interactor=answer_quiz_question_interactor,
            group_id=group_id,
        )
    return vk_ok_response()


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


async def _handle_registered_user_message(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
    intent_classifier: IUserMessageIntentClassifier,
    get_vk_user_tasks_interactor: GetVKUserTasksHandler,
    get_quiz_first_question_interactor: GetQuizFirstQuestionHandler,
    answer_quiz_question_interactor: AnswerQuizQuestionHandler,
    group_id: int,
) -> None:
    """Обрабатывает интерактивное меню и текстовые intent-ы зарегистрированного пользователя."""

    # Проверяем payload кнопки — приоритет выше текстового intent
    button_payload = data.get_button_payload()
    if button_payload is not None:
        action = button_payload.get("action")
        if action == "start_quiz":
            tasks_id = button_payload.get("tasks_id")
            if isinstance(tasks_id, int):
                await _handle_start_quiz(
                    data=data,
                    result=result,
                    tasks_id=tasks_id,
                    message_client=message_client,
                    get_quiz_first_question_interactor=get_quiz_first_question_interactor,
                    get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
                )
                return
        elif action == "skip_quiz":
            await _handle_skip_quiz(
                data=data,
                result=result,
                message_client=message_client,
                get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
            )
            return
        elif action == "quiz_answer":
            quiz_questions_id = button_payload.get("quiz_questions_id")
            option_id = button_payload.get("option_id")
            if isinstance(quiz_questions_id, int) and isinstance(option_id, int):
                await _handle_quiz_answer(
                    data=data,
                    result=result,
                    quiz_questions_id=quiz_questions_id,
                    quiz_question_options_id=option_id,
                    message_client=message_client,
                    answer_quiz_question_interactor=answer_quiz_question_interactor,
                )
                return

    message_text = data.get_message_text()
    classified = await intent_classifier.classify(text=message_text)
    if classified.intent == UserMessageIntent.TASKS:
        tasks_result = await get_vk_user_tasks_interactor(
            command_data=GetVKUserTasksCommand(vk_user_id=result.registration.vk_user_id),
        )
        if tasks_result.active_quiz is not None:
            quiz = tasks_result.active_quiz
            await send_vk_user_message(
                data=data,
                vk_user_id=result.registration.vk_user_id,
                users_id=result.registration.users_id,
                message=build_quiz_offer_message(
                    task_name=quiz.task_name,
                    points=quiz.points,
                ),
                keyboard=build_quiz_offer_keyboard(tasks_id=quiz.tasks_id),
                message_client=message_client,
                log_message="Предложение квиза VK",
            )
            return
        response = build_tasks_message(tasks=tasks_result.tasks)
    elif classified.intent == UserMessageIntent.REFERRAL:
        response = build_referral_link_message(
            vk_user_id=result.registration.vk_user_id,
            group_id=group_id,
        )
    else:
        response = _build_registered_user_response(
            intent=classified.intent,
            balance_points=result.registration.balance_points,
        )
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=response,
        message_client=message_client,
        log_message="Ответ VK зарегистрированному пользователю",
    )


async def _process_referral_on_registration(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    process_referral_interactor: ProcessReferralHandler,
    message_client: IVKMessageClient,
) -> None:
    """Обрабатывает реф-ссылку при первой регистрации нового пользователя.

    VK передаёт ref-параметр ссылки в message.payload как {'ref': '<value>'}.
    """
    raw_ref = data.get_ref_key()
    if raw_ref is None:
        return
    try:
        inviter_vk_user_id = int(raw_ref)
    except (ValueError, TypeError):
        return

    referral_result = await process_referral_interactor(
        command_data=ProcessReferralCommand(
            invited_vk_user_id=result.registration.vk_user_id,
            inviter_vk_user_id=inviter_vk_user_id,
        ),
    )

    if not referral_result.created or referral_result.inviter_users_id is None:
        return
    if referral_result.inviter_balance_points is None:
        return

    # Уведомляем пригласившего о +30 ✦
    await send_vk_user_message(
        data=data,
        vk_user_id=referral_result.inviter_vk_user_id,
        users_id=referral_result.inviter_users_id,
        message=build_referral_bonus_message(
            bonus_points=referral_result.bonus_points,
            balance_points=referral_result.inviter_balance_points,
        ),
        message_client=message_client,
        log_message="Уведомление о реферальном бонусе VK",
    )

    # Уведомление о новом уровне после реферального бонуса
    if referral_result.level_up is not None:
        await send_vk_user_message(
            data=data,
            vk_user_id=referral_result.inviter_vk_user_id,
            users_id=referral_result.inviter_users_id,
            message=build_level_up_message(
                new_level=referral_result.level_up,
                level_name=get_level_name(referral_result.level_up),
                balance_points=referral_result.inviter_balance_points,
            ),
            message_client=message_client,
            log_message="Уведомление о новом уровне (реферал) VK",
        )

    # Дополнительно уведомляем о milestone-бонусе, если достигнут
    if referral_result.milestone_reached is not None and referral_result.milestone_bonus_points is not None:
        # Баланс после milestone — складываем оба бонуса
        milestone_balance = referral_result.inviter_balance_points
        await send_vk_user_message(
            data=data,
            vk_user_id=referral_result.inviter_vk_user_id,
            users_id=referral_result.inviter_users_id,
            message=build_referral_milestone_message(
                milestone_count=referral_result.milestone_reached,
                bonus_points=referral_result.milestone_bonus_points,
                balance_points=milestone_balance,
            ),
            message_client=message_client,
            log_message="Уведомление о milestone рефералки VK",
        )


async def _handle_start_quiz(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    tasks_id: int,
    message_client: IVKMessageClient,
    get_quiz_first_question_interactor: GetQuizFirstQuestionHandler,
    get_vk_user_tasks_interactor: GetVKUserTasksHandler,
) -> None:
    question = await get_quiz_first_question_interactor(
        command_data=GetQuizFirstQuestionCommand(
            tasks_id=tasks_id,
            vk_user_id=result.registration.vk_user_id,
        ),
    )
    if question is None:
        await send_vk_user_message(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            message=build_quiz_unavailable_message(),
            message_client=message_client,
            log_message="Сообщение о недоступной викторине VK",
        )

        # Квиз уже пройден, недоступен или вопросов нет — показываем актуальный список заданий
        tasks_result = await get_vk_user_tasks_interactor(
            command_data=GetVKUserTasksCommand(vk_user_id=result.registration.vk_user_id),
        )
        await send_vk_user_message(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            message=build_tasks_message(tasks=tasks_result.tasks),
            message_client=message_client,
            log_message="Квиз не найден при старте — показываем список заданий",
        )
        return

    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_quiz_question_message(
            question_text=question.question_text,
            question_number=question.question_number,
            total_questions=question.total_questions,
        ),
        keyboard=build_quiz_question_keyboard(
            quiz_questions_id=question.quiz_questions_id,
            options=[(opt.quiz_question_options_id, opt.option_text) for opt in question.options],
        ),
        message_client=message_client,
        log_message="Вопрос квиза VK",
    )


async def _handle_skip_quiz(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
    get_vk_user_tasks_interactor: GetVKUserTasksHandler,
) -> None:
    tasks_result = await get_vk_user_tasks_interactor(
        command_data=GetVKUserTasksCommand(vk_user_id=result.registration.vk_user_id),
    )
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_tasks_message(tasks=tasks_result.tasks),
        message_client=message_client,
        log_message="Список заданий VK после пропуска квиза",
    )


async def _handle_quiz_answer(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    quiz_questions_id: int,
    quiz_question_options_id: int,
    message_client: IVKMessageClient,
    answer_quiz_question_interactor: AnswerQuizQuestionHandler,
) -> None:
    answer_result = await answer_quiz_question_interactor(
        command_data=AnswerQuizQuestionCommand(
            vk_user_id=result.registration.vk_user_id,
            quiz_questions_id=quiz_questions_id,
            quiz_question_options_id=quiz_question_options_id,
        ),
    )

    if answer_result.invalid_payload:
        return

    if answer_result.quiz_unavailable:
        await send_vk_user_message(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            message=build_quiz_unavailable_message(),
            message_client=message_client,
            log_message="Сообщение о недоступной викторине VK",
        )
        return

    # Обратная связь по правильности ответа (не показываем при повторном нажатии)
    if not answer_result.already_answered:
        await send_vk_user_message(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            message=build_quiz_answer_result_message(
                is_correct=answer_result.is_correct,
                correct_option_text=answer_result.correct_option_text
                if not answer_result.is_correct
                else None,
            ),
            message_client=message_client,
            log_message="Результат ответа на вопрос квиза VK",
        )

    # Если квиз завершён — показываем награду с главным меню
    if answer_result.task_completed and answer_result.balance_points is not None:
        await send_vk_user_message(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            message=build_quiz_completed_message(
                points_awarded=answer_result.points_awarded,
                balance_points=answer_result.balance_points,
            ),
            message_client=message_client,
            log_message="Сообщение о завершении квиза VK",
        )
        if answer_result.level_up is not None:
            await send_vk_user_message(
                data=data,
                vk_user_id=result.registration.vk_user_id,
                users_id=result.registration.users_id,
                message=build_level_up_message(
                    new_level=answer_result.level_up,
                    level_name=get_level_name(answer_result.level_up),
                    balance_points=answer_result.balance_points,
                ),
                message_client=message_client,
                log_message="Сообщение о новом уровне (квиз) VK",
            )
        await send_week_completion_reward_if_needed(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            week_number=answer_result.week_completion_week_number,
            points_awarded=answer_result.week_completion_points_awarded,
            balance_points=answer_result.week_completion_balance_points,
            level_up=answer_result.week_completion_level_up,
            message_client=message_client,
        )
        await send_quiz_streak_reward_if_needed(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            streak_count=answer_result.quiz_streak_count,
            points_awarded=answer_result.quiz_streak_points_awarded,
            balance_points=answer_result.quiz_streak_balance_points,
            level_up=answer_result.quiz_streak_level_up,
            message_client=message_client,
        )
        return

    # Если есть следующий вопрос — показываем его
    next_q = answer_result.next_question
    if next_q is not None:
        await send_vk_user_message(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            message=build_quiz_question_message(
                question_text=next_q.question_text,
                question_number=next_q.question_number,
                total_questions=next_q.total_questions,
            ),
            keyboard=build_quiz_question_keyboard(
                quiz_questions_id=next_q.quiz_questions_id,
                options=[(opt.quiz_question_options_id, opt.option_text) for opt in next_q.options],
            ),
            message_client=message_client,
            log_message="Следующий вопрос квиза VK",
        )


def _build_registered_user_response(
    *,
    intent: UserMessageIntent,
    balance_points: int,
) -> VKMessageText:
    if intent == UserMessageIntent.BALANCE:
        return build_balance_message(balance_points=balance_points)
    if intent == UserMessageIntent.HELP:
        return build_help_message()
    return build_free_text_fallback_message()
