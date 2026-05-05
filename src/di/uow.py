from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from application.interface.uow import IUnitOfWork
from infrastructure.database.uow import SQLAlchemyBaseUoW
from infrastructure.uow.base import UnitOfWork


class UoWProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_uow(self, session: AsyncSession) -> IUnitOfWork:
        db_uow = SQLAlchemyBaseUoW(session=session)
        return UnitOfWork((db_uow,))
