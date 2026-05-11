from collections.abc import Sequence

from application.interface.uow import IUnitOfWork


class UnitOfWork(IUnitOfWork):
    """Композитный Unit of Work для нескольких инфраструктурных UoW."""

    def __init__(self, uows: Sequence[IUnitOfWork]) -> None:
        self._uows = uows

    async def commit(self) -> None:
        for uow in self._uows:
            await uow.commit()

    async def rollback(self) -> None:
        for uow in self._uows:
            await uow.rollback()
