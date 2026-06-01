from collections.abc import AsyncIterator, Sequence
from contextlib import AbstractAsyncContextManager, AsyncExitStack, asynccontextmanager

from application.interface.uow import IUnitOfWork


class UnitOfWork(IUnitOfWork):
    """Композитный Unit of Work для нескольких инфраструктурных UoW."""

    def __init__(self, uows: Sequence[IUnitOfWork]) -> None:
        self._uows = uows

    def begin_nested(self) -> AbstractAsyncContextManager[object]:
        return self._begin_nested()

    @asynccontextmanager
    async def _begin_nested(self) -> AsyncIterator[None]:
        async with AsyncExitStack() as stack:
            for uow in self._uows:
                await stack.enter_async_context(uow.begin_nested())
            yield

    async def commit(self) -> None:
        for uow in self._uows:
            await uow.commit()

    async def rollback(self) -> None:
        for uow in self._uows:
            await uow.rollback()
