from abc import abstractmethod
from contextlib import AbstractAsyncContextManager
from typing import Protocol


class IUnitOfWork(Protocol):
    """Минимальный контракт атомарного завершения application-сценария."""

    @abstractmethod
    def begin_nested(self) -> AbstractAsyncContextManager[object]:
        """Открывает savepoint внутри текущей транзакции."""

        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        """Фиксирует изменения, сделанные в рамках текущего сценария."""

        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Откатывает изменения текущего сценария."""

        raise NotImplementedError
