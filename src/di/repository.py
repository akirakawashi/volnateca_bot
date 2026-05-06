from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from application.interface.repositories.users import IUserRepository
from infrastructure.database.repositories.users import UserRepository


class RepositoriesProvider(Provider):
    @provide(scope=Scope.REQUEST, provides=IUserRepository)
    def get_user_repository(
        self,
        session: AsyncSession,
    ) -> UserRepository:
        return UserRepository(session=session)
