from dataclasses import dataclass

from fastapi import HTTPException, status
from fastapi.responses import PlainTextResponse

from application.command.answer_quiz_question import AnswerQuizQuestionHandler
from application.command.capture_vk_referral_intent import CaptureVKReferralIntentHandler
from application.command.complete_vk_comment_task import CompleteVKCommentTaskHandler
from application.command.complete_vk_like_task import CompleteVKLikeTaskHandler
from application.command.complete_vk_poll_task import CompleteVKPollTaskHandler
from application.command.complete_vk_repost_task import CompleteVKRepostTaskHandler
from application.command.complete_vk_subscription_task import CompleteVKSubscriptionTaskHandler
from application.command.ensure_vk_poll_task import EnsureVKPollTaskHandler
from application.command.get_quiz_first_question import GetQuizFirstQuestionHandler
from application.command.get_store_catalog import GetStoreCatalogHandler, GetStorePrizeCardHandler
from application.command.get_vk_user_tasks import GetVKUserTasksHandler
from application.command.register_vk_user_with_referral_context import RegisterVKUserWithReferralContextHandler
from application.command.task_promo_code import (
    ActivateTaskPromoCodeHandler,
    CancelTaskPromoCodeHandler,
    GetTaskPromoCodeWaitHandler,
    StartTaskPromoCodeHandler,
)
from application.interface.clients import IVKMessageClient
from application.interface.repositories.users import IUserRepository
from application.interface.services import IVKMessageTemplateService
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.handlers import (
    handle_comment_callback,
    handle_confirmation_callback,
    handle_ignored_callback,
    handle_like_callback,
    handle_poll_vote_callback,
    handle_registration_callback,
    handle_repost_callback,
    handle_subscription_callback,
    handle_wall_post_callback,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.sender import bind_vk_message_template_service
from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload
from settings.vk import TaskTypeImagesSettings, VKSettings


@dataclass(slots=True, frozen=True, kw_only=True)
class VKCallbackDispatcher:
    """Единая точка маршрутизации VK Callback API событий.

    Сначала проверяет group_id, затем confirmation или secret, после чего
    передаёт типизированный payload в обработчик конкретной группы событий.
    """

    vk_settings: VKSettings
    task_images_settings: TaskTypeImagesSettings
    complete_vk_repost_task_interactor: CompleteVKRepostTaskHandler
    complete_vk_subscription_task_interactor: CompleteVKSubscriptionTaskHandler
    complete_vk_like_task_interactor: CompleteVKLikeTaskHandler
    complete_vk_comment_task_interactor: CompleteVKCommentTaskHandler
    complete_vk_poll_task_interactor: CompleteVKPollTaskHandler
    ensure_vk_poll_task_interactor: EnsureVKPollTaskHandler
    get_store_catalog_interactor: GetStoreCatalogHandler
    get_store_prize_card_interactor: GetStorePrizeCardHandler
    get_vk_user_tasks_interactor: GetVKUserTasksHandler
    get_quiz_first_question_interactor: GetQuizFirstQuestionHandler
    answer_quiz_question_interactor: AnswerQuizQuestionHandler
    start_task_promo_code_interactor: StartTaskPromoCodeHandler
    activate_task_promo_code_interactor: ActivateTaskPromoCodeHandler
    cancel_task_promo_code_interactor: CancelTaskPromoCodeHandler
    get_task_promo_code_wait_interactor: GetTaskPromoCodeWaitHandler
    capture_vk_referral_intent_interactor: CaptureVKReferralIntentHandler
    register_vk_user_with_referral_context_interactor: RegisterVKUserWithReferralContextHandler
    vk_message_client: IVKMessageClient
    vk_message_template_service: IVKMessageTemplateService
    user_repository: IUserRepository

    async def handle(self, data: VKCallbackSchema) -> PlainTextResponse:
        """Валидирует callback и возвращает VK-совместимый plain text response."""
        with bind_vk_message_template_service(self.vk_message_template_service):
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

            if payload.is_comment_event():
                return await handle_comment_callback(
                    data=payload,
                    interactor_complete=self.complete_vk_comment_task_interactor,
                    message_client=self.vk_message_client,
                )

            if payload.is_poll_vote_event():
                return await handle_poll_vote_callback(
                    data=payload,
                    interactor_complete=self.complete_vk_poll_task_interactor,
                    message_client=self.vk_message_client,
                )

            if payload.is_repost():
                return await handle_repost_callback(
                    data=payload,
                    interactor=self.complete_vk_repost_task_interactor,
                    interactor_like=self.complete_vk_like_task_interactor,
                    message_client=self.vk_message_client,
                )

            if payload.is_subscription_event():
                return await handle_subscription_callback(
                    data=payload,
                    interactor=self.complete_vk_subscription_task_interactor,
                    message_client=self.vk_message_client,
                )

            if payload.is_wall_post_event():
                return await handle_wall_post_callback(
                    data=payload,
                    interactor=self.ensure_vk_poll_task_interactor,
                )

            if payload.is_registration_event():
                return await handle_registration_callback(
                    data=payload,
                    get_vk_user_tasks_interactor=self.get_vk_user_tasks_interactor,
                    get_store_catalog_interactor=self.get_store_catalog_interactor,
                    get_store_prize_card_interactor=self.get_store_prize_card_interactor,
                    get_quiz_first_question_interactor=self.get_quiz_first_question_interactor,
                    answer_quiz_question_interactor=self.answer_quiz_question_interactor,
                    start_task_promo_code_interactor=self.start_task_promo_code_interactor,
                    activate_task_promo_code_interactor=self.activate_task_promo_code_interactor,
                    cancel_task_promo_code_interactor=self.cancel_task_promo_code_interactor,
                    get_task_promo_code_wait_interactor=self.get_task_promo_code_wait_interactor,
                    capture_referral_intent_interactor=self.capture_vk_referral_intent_interactor,
                    register_with_referral_context_interactor=(
                        self.register_vk_user_with_referral_context_interactor
                    ),
                    group_id=self.vk_settings.GROUP_ID,
                    task_images_settings=self.task_images_settings,
                    message_client=self.vk_message_client,
                    user_repository=self.user_repository,
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
