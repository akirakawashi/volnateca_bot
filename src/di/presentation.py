from dishka import Provider, Scope, provide

from application.command.complete_vk_like_task import CompleteVKLikeTaskHandler
from application.command.complete_vk_repost_task import CompleteVKRepostTaskHandler
from application.command.complete_vk_subscription_task import CompleteVKSubscriptionTaskHandler
from application.command.create_vk_post_tasks import CreateVKPostTasksHandler
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionHandler,
)
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
        create_vk_post_tasks_interactor: CreateVKPostTasksHandler,
        complete_vk_like_task_interactor: CompleteVKLikeTaskHandler,
    ) -> VKCallbackDispatcher:
        return VKCallbackDispatcher(
            vk_settings=vk_settings,
            register_vk_user_and_check_subscription_interactor=(
                register_vk_user_and_check_subscription_interactor
            ),
            complete_vk_repost_task_interactor=complete_vk_repost_task_interactor,
            complete_vk_subscription_task_interactor=complete_vk_subscription_task_interactor,
            create_vk_post_tasks_interactor=create_vk_post_tasks_interactor,
            complete_vk_like_task_interactor=complete_vk_like_task_interactor,
        )
