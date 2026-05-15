from dataclasses import dataclass

from application.base_interactor import Interactor
from application.admin.interface.db_manager import IDBManager


# TODO: удалить TruncateDBCommand и TruncateDBHandler перед релизом — только для локальной отладки.
@dataclass(slots=True, frozen=True, kw_only=True)
class TruncateDBCommand:
    pass


class TruncateDBHandler(Interactor[TruncateDBCommand, None]):
    """Полностью очищает все таблицы БД. Только для локальной разработки."""

    def __init__(self, db_manager: IDBManager) -> None:
        self._db_manager = db_manager

    async def __call__(self, command_data: TruncateDBCommand) -> None:
        await self._db_manager.truncate_all()
