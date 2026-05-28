from dishka import Provider, Scope, provide

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
from application.interface.clients import IVKMessageClient
from application.interface.repositories.users import IUserRepository
from application.interface.services import IVKMessageTemplateService
from presentation.http.routers.v1.routers.vk_callbacks.dispatcher import VKCallbackDispatcher
from settings.vk import TaskTypeImagesSettings, VKSettings


class PresentationProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_vk_callback_dispatcher(
        self,
        vk_settings: VKSettings,
        task_images_settings: TaskTypeImagesSettings,
        complete_vk_repost_task_interactor: CompleteVKRepostTaskHandler,
        complete_vk_subscription_task_interactor: CompleteVKSubscriptionTaskHandler,
        complete_vk_like_task_interactor: CompleteVKLikeTaskHandler,
        complete_vk_comment_task_interactor: CompleteVKCommentTaskHandler,
        complete_vk_poll_task_interactor: CompleteVKPollTaskHandler,
        ensure_vk_poll_task_interactor: EnsureVKPollTaskHandler,
        get_store_catalog_interactor: GetStoreCatalogHandler,
        get_store_prize_card_interactor: GetStorePrizeCardHandler,
        get_vk_user_tasks_interactor: GetVKUserTasksHandler,
        get_quiz_first_question_interactor: GetQuizFirstQuestionHandler,
        answer_quiz_question_interactor: AnswerQuizQuestionHandler,
        capture_vk_referral_intent_interactor: CaptureVKReferralIntentHandler,
        register_vk_user_with_referral_context_interactor: RegisterVKUserWithReferralContextHandler,
        vk_message_client: IVKMessageClient,
        vk_message_template_service: IVKMessageTemplateService,
        user_repository: IUserRepository,
    ) -> VKCallbackDispatcher:
        return VKCallbackDispatcher(
            vk_settings=vk_settings,
            task_images_settings=task_images_settings,
            complete_vk_repost_task_interactor=complete_vk_repost_task_interactor,
            complete_vk_subscription_task_interactor=complete_vk_subscription_task_interactor,
            complete_vk_like_task_interactor=complete_vk_like_task_interactor,
            complete_vk_comment_task_interactor=complete_vk_comment_task_interactor,
            complete_vk_poll_task_interactor=complete_vk_poll_task_interactor,
            ensure_vk_poll_task_interactor=ensure_vk_poll_task_interactor,
            get_store_catalog_interactor=get_store_catalog_interactor,
            get_store_prize_card_interactor=get_store_prize_card_interactor,
            get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
            get_quiz_first_question_interactor=get_quiz_first_question_interactor,
            answer_quiz_question_interactor=answer_quiz_question_interactor,
            capture_vk_referral_intent_interactor=capture_vk_referral_intent_interactor,
            register_vk_user_with_referral_context_interactor=(
                register_vk_user_with_referral_context_interactor
            ),
            vk_message_client=vk_message_client,
            vk_message_template_service=vk_message_template_service,
            user_repository=user_repository,
        )
