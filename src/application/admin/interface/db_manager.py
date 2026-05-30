# TODO DEV: удалить IDBManager перед релизом — используется только для truncate.

from abc import ABC, abstractmethod


class IDBManager(ABC):
    @abstractmethod
    async def truncate_all(self) -> None:
        """Очищает все таблицы и сбрасывает последовательности."""
        raise NotImplementedError
