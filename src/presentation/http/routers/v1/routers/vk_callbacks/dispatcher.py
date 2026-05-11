from dataclasses import dataclass

from fastapi import HTTPException, status
from fastapi.responses import PlainTextResponse

from application.command.answer_quiz_question import AnswerQuizQuestionHandler
from application.command.complete_vk_like_task import CompleteVKLikeTaskHandler
from application.command.complete_vk_repost_task import CompleteVKRepostTaskHandler
from application.command.complete_vk_subscription_task import CompleteVKSubscriptionTaskHandler
from application.command.create_vk_post_tasks import CreateVKPostTasksHandler
from application.command.get_quiz_first_question import GetQuizFirstQuestionHandler
from application.command.get_vk_user_tasks import GetVKUserTasksHandler
from application.command.process_referral import ProcessReferralHandler
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionHandler,
)
from application.interface.clients import IVKMessageClient
from application.interface.services import IUserMessageIntentClassifier
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.handlers import (
    handle_confirmation_callback,
    handle_ignored_callback,
    handle_like_callback,
    handle_registration_callback,
    handle_repost_callback,
    handle_subscription_callback,
    handle_wall_post_new_callback,
)
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from settings.vk import VKSettings


@dataclass(slots=True, frozen=True, kw_only=True)
class VKCallbackDispatcher:
    vk_settings: VKSettings
    register_vk_user_and_check_subscription_interactor: RegisterVKUserAndCheckSubscriptionHandler
    complete_vk_repost_task_interactor: CompleteVKRepostTaskHandler
    complete_vk_subscription_task_interactor: CompleteVKSubscriptionTaskHandler
    create_vk_post_tasks_interactor: CreateVKPostTasksHandler
    complete_vk_like_task_interactor: CompleteVKLikeTaskHandler
    get_vk_user_tasks_interactor: GetVKUserTasksHandler
    get_quiz_first_question_interactor: GetQuizFirstQuestionHandler
    answer_quiz_question_interactor: AnswerQuizQuestionHandler
    process_referral_interactor: ProcessReferralHandler
    vk_message_client: IVKMessageClient
    user_message_intent_classifier: IUserMessageIntentClassifier

    async def handle(self, data: VKCallbackSchema) -> PlainTextResponse:
        payload = VKCallbackPayload(data=data)
        self._validate_group(payload=payload)

        if payload.is_confirmation():
            return handle_confirmation_callback(vk_settings=self.vk_settings)

        self._validate_secret(payload=payload)

        if payload.is_like():
            return await handle_like_callback(
                data=payload,
                interactor_complete=self.complete_vk_like_task_interactor,
                message_client=self.vk_message_client,
            )

        if payload.is_wall_post_new():
            return await handle_wall_post_new_callback(
                data=payload,
                interactor=self.create_vk_post_tasks_interactor,
            )

        if payload.is_repost():
            return await handle_repost_callback(
                data=payload,
                interactor=self.complete_vk_repost_task_interactor,
                message_client=self.vk_message_client,
            )

        if payload.is_subscription_event():
            return await handle_subscription_callback(
                data=payload,
                interactor=self.complete_vk_subscription_task_interactor,
                message_client=self.vk_message_client,
            )

        if payload.is_registration_event():
            return await handle_registration_callback(
                data=payload,
                interactor=self.register_vk_user_and_check_subscription_interactor,
                get_vk_user_tasks_interactor=self.get_vk_user_tasks_interactor,
                get_quiz_first_question_interactor=self.get_quiz_first_question_interactor,
                answer_quiz_question_interactor=self.answer_quiz_question_interactor,
                process_referral_interactor=self.process_referral_interactor,
                group_id=self.vk_settings.GROUP_ID,
                message_client=self.vk_message_client,
                intent_classifier=self.user_message_intent_classifier,
            )

        return handle_ignored_callback(data=payload)

    def _validate_group(self, payload: VKCallbackPayload) -> None:
        if payload.is_expected_group(expected_group_id=self.vk_settings.GROUP_ID):
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неожиданный ID сообщества VK",
        )

    def _validate_secret(self, payload: VKCallbackPayload) -> None:
        if payload.has_valid_secret(expected_secret=self.vk_settings.SECRET_KEY):
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Некорректный секретный ключ события VK",
        )
