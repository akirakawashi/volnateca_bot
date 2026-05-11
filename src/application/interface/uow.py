from abc import abstractmethod
from typing import Protocol


class IUnitOfWork(Protocol):
    """Минимальный контракт атомарного завершения application-сценария."""

    @abstractmethod
    async def commit(self) -> None:
        """Фиксирует изменения, сделанные в рамках текущего сценария."""

        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Откатывает изменения текущего сценария."""

        raise NotImplementedError
