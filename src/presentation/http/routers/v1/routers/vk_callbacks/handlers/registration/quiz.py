"""Обработчики квиза: старт, пропуск, ответ на вопрос и финальные начисления."""

from application.command.answer_quiz_question import (
    AnswerQuizQuestionCommand,
    AnswerQuizQuestionHandler,
)
from application.command.get_quiz_first_question import (
    GetQuizFirstQuestionCommand,
    GetQuizFirstQuestionHandler,
)
from application.command.get_vk_user_tasks import (
    GetVKUserTasksCommand,
    GetVKUserTasksHandler,
)
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionDTO,
)
from application.interface.clients import IVKMessageClient
from domain.services.level import get_level_name
from presentation.http.routers.v1.routers.vk_callbacks.handlers.achievement import (
    send_project_completion_reward_if_needed,
    send_week_completion_reward_if_needed,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.tasks import (
    send_tasks_catalog,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards import (
    build_quiz_question_keyboard,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages import (
    build_level_up_message,
    build_quiz_answer_result_message,
    build_quiz_completed_message,
    build_quiz_failed_message,
    build_quiz_question_message,
    build_quiz_unavailable_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload
from settings.vk.task_images import TaskTypeImagesSettings


async def handle_start_quiz(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    tasks_id: int,
    message_client: IVKMessageClient,
    get_quiz_first_question_interactor: GetQuizFirstQuestionHandler,
    get_vk_user_tasks_interactor: GetVKUserTasksHandler,
    task_images_settings: TaskTypeImagesSettings,
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
        await send_tasks_catalog(
            data=data,
            result=result,
            tasks_result=tasks_result,
            message_client=message_client,
            task_images_settings=task_images_settings,
            carousel_log_message="Карусель заданий VK после недоступного квиза",
            list_log_message="Квиз не найден при старте — показываем список заданий",
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
        attachment=question.image_attachment,
        dont_parse_links=True,
    )


async def handle_skip_quiz(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
    get_vk_user_tasks_interactor: GetVKUserTasksHandler,
    task_images_settings: TaskTypeImagesSettings,
) -> None:
    tasks_result = await get_vk_user_tasks_interactor(
        command_data=GetVKUserTasksCommand(vk_user_id=result.registration.vk_user_id),
    )
    await send_tasks_catalog(
        data=data,
        result=result,
        tasks_result=tasks_result,
        message_client=message_client,
        task_images_settings=task_images_settings,
        carousel_log_message="Карусель заданий VK после пропуска квиза",
        list_log_message="Список заданий VK после пропуска квиза",
    )


async def handle_quiz_answer(
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

    if answer_result.already_answered:
        return

    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_quiz_answer_result_message(
            is_correct=answer_result.is_correct,
            correct_option_text=answer_result.correct_option_text if not answer_result.is_correct else None,
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
        await send_project_completion_reward_if_needed(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            points_awarded=answer_result.project_completion_points_awarded,
            balance_points=answer_result.project_completion_balance_points,
            level_up=answer_result.project_completion_level_up,
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
            attachment=next_q.image_attachment,
            dont_parse_links=True,
        )
        return

    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_quiz_failed_message(),
        message_client=message_client,
        log_message="Сообщение о завершении квиза без награды VK",
    )
