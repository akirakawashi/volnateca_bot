from dishka import Provider, Scope, provide

from application.command.complete_vk_like_task import CompleteVKLikeTaskHandler
from application.command.complete_vk_repost_task import CompleteVKRepostTaskHandler
from application.command.complete_vk_subscription_task import CompleteVKSubscriptionTaskHandler
from application.command.create_vk_post_tasks import CreateVKPostTasksHandler
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionHandler,
)
from application.command.register_vk_user import RegisterVKUserHandler
from application.interface.clients import IVKUserClient
from application.interface.repositories.tasks import ITaskCompletionRepository
from application.interface.repositories.users import IUserRepository
from application.interface.uow import IUnitOfWork
from settings.vk import VKSettings


class InteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_register_vk_user_handler(
        self,
        repository: IUserRepository,
        uow: IUnitOfWork,
        vk_user_client: IVKUserClient,
    ) -> RegisterVKUserHandler:
        return RegisterVKUserHandler(
            repository=repository,
            uow=uow,
            vk_user_client=vk_user_client,
        )

    @provide(scope=Scope.REQUEST)
    def get_register_vk_user_and_check_subscription_handler(
        self,
        register_vk_user_interactor: RegisterVKUserHandler,
        complete_vk_subscription_task_interactor: CompleteVKSubscriptionTaskHandler,
    ) -> RegisterVKUserAndCheckSubscriptionHandler:
        return RegisterVKUserAndCheckSubscriptionHandler(
            register_vk_user_interactor=register_vk_user_interactor,
            complete_vk_subscription_task_interactor=complete_vk_subscription_task_interactor,
        )

    @provide(scope=Scope.REQUEST)
    def get_complete_vk_repost_task_handler(
        self,
        repository: ITaskCompletionRepository,
        uow: IUnitOfWork,
    ) -> CompleteVKRepostTaskHandler:
        return CompleteVKRepostTaskHandler(
            repository=repository,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_complete_vk_subscription_task_handler(
        self,
        repository: ITaskCompletionRepository,
        uow: IUnitOfWork,
        vk_user_client: IVKUserClient,
        vk_settings: VKSettings,
    ) -> CompleteVKSubscriptionTaskHandler:
        return CompleteVKSubscriptionTaskHandler(
            repository=repository,
            uow=uow,
            vk_user_client=vk_user_client,
            required_subscription_group_id=vk_settings.required_subscription_group_id,
        )

    @provide(scope=Scope.REQUEST)
    def get_create_vk_post_tasks_handler(
        self,
        repository: ITaskCompletionRepository,
        uow: IUnitOfWork,
    ) -> CreateVKPostTasksHandler:
        return CreateVKPostTasksHandler(
            repository=repository,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_complete_vk_like_task_handler(
        self,
        repository: ITaskCompletionRepository,
        uow: IUnitOfWork,
    ) -> CompleteVKLikeTaskHandler:
        return CompleteVKLikeTaskHandler(
            repository=repository,
            uow=uow,
        )
