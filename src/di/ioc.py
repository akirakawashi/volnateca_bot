from dishka import Provider, Scope, provide

from application.command.register_vk_user import RegisterVKUserHandler
from application.interface.clients import IVKUserClient
from application.interface.repositories.users import IUserRepository
from application.interface.uow import IUnitOfWork


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
