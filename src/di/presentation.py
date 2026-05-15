from dishka import Provider, Scope, provide

from application.command.answer_quiz_question import AnswerQuizQuestionHandler
from application.command.complete_vk_comment_task import CompleteVKCommentTaskHandler
from application.command.complete_vk_like_task import CompleteVKLikeTaskHandler
from application.command.complete_vk_repost_task import CompleteVKRepostTaskHandler
from application.command.complete_vk_subscription_task import CompleteVKSubscriptionTaskHandler
from application.command.get_quiz_first_question import GetQuizFirstQuestionHandler
from application.command.get_vk_user_tasks import GetVKUserTasksHandler
from application.command.process_referral import ProcessReferralHandler
from application.command.record_vk_user_activity import RecordVKUserActivityHandler
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionHandler,
)
from application.interface.clients import IVKMessageClient
from application.interface.services import IUserMessageIntentClassifier
from presentation.http.routers.v1.routers.vk_callbacks.dispatcher import VKCallbackDispatcher
from settings.vk import VKSettings


class PresentationProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_vk_callback_dispatcher(
        self,
        vk_settings: VKSettings,
        register_vk_user_and_check_subscription_interactor: RegisterVKUserAndCheckSubscriptionHandler,
        complete_vk_repost_task_interactor: CompleteVKRepostTaskHandler,
        complete_vk_subscription_task_interactor: CompleteVKSubscriptionTaskHandler,
        complete_vk_like_task_interactor: CompleteVKLikeTaskHandler,
        complete_vk_comment_task_interactor: CompleteVKCommentTaskHandler,
        get_vk_user_tasks_interactor: GetVKUserTasksHandler,
        get_quiz_first_question_interactor: GetQuizFirstQuestionHandler,
        answer_quiz_question_interactor: AnswerQuizQuestionHandler,
        process_referral_interactor: ProcessReferralHandler,
        record_vk_user_activity_interactor: RecordVKUserActivityHandler,
        vk_message_client: IVKMessageClient,
        user_message_intent_classifier: IUserMessageIntentClassifier,
    ) -> VKCallbackDispatcher:
        return VKCallbackDispatcher(
            vk_settings=vk_settings,
            register_vk_user_and_check_subscription_interactor=(
                register_vk_user_and_check_subscription_interactor
            ),
            complete_vk_repost_task_interactor=complete_vk_repost_task_interactor,
            complete_vk_subscription_task_interactor=complete_vk_subscription_task_interactor,
            complete_vk_like_task_interactor=complete_vk_like_task_interactor,
            complete_vk_comment_task_interactor=complete_vk_comment_task_interactor,
            get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
            get_quiz_first_question_interactor=get_quiz_first_question_interactor,
            answer_quiz_question_interactor=answer_quiz_question_interactor,
            process_referral_interactor=process_referral_interactor,
            record_vk_user_activity_interactor=record_vk_user_activity_interactor,
            vk_message_client=vk_message_client,
            user_message_intent_classifier=user_message_intent_classifier,
        )
