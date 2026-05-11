from sqlalchemy.ext.asyncio import AsyncSession

from application.interface.uow import IUnitOfWork


class SQLAlchemyBaseUoW(IUnitOfWork):
    """Unit of Work поверх одной AsyncSession SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
