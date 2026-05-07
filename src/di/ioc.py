from dishka import Provider, Scope, provide

from application.command.complete_vk_subscription_task import CompleteVKSubscriptionTaskHandler
from application.command.complete_vk_repost_task import CompleteVKRepostTaskHandler
from application.command.create_vk_repost_task_from_wall_post import (
    CreateVKRepostTaskFromWallPostHandler,
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
    def get_complete_vk_repost_task_handler(
        self,
        repository: ITaskCompletionRepository,
        uow: IUnitOfWork,
        vk_user_client: IVKUserClient,
        vk_settings: VKSettings,
    ) -> CompleteVKRepostTaskHandler:
        return CompleteVKRepostTaskHandler(
            repository=repository,
            uow=uow,
            vk_user_client=vk_user_client,
            required_subscription_group_id=vk_settings.required_subscription_group_id,
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
    def get_create_vk_repost_task_from_wall_post_handler(
        self,
        repository: ITaskCompletionRepository,
        uow: IUnitOfWork,
    ) -> CreateVKRepostTaskFromWallPostHandler:
        return CreateVKRepostTaskFromWallPostHandler(
            repository=repository,
            uow=uow,
        )
