from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.admin.interface.broadcast_recipients import IBroadcastRecipientReader
from application.common.dto.user import ActiveVKUserDTO
from infrastructure.database.repositories.users import UserRepository


class SQLAlchemyBroadcastRecipientReader(IBroadcastRecipientReader):
    def __init__(self, session_pool: async_sessionmaker[AsyncSession]) -> None:
        self._session_pool = session_pool

    async def count_active_users(self) -> int:
        async with self._session_pool() as session:
            return await UserRepository(session=session).count_active_users()

    async def list_active_users_page(
        self,
        *,
        after_users_id: int | None,
        limit: int,
    ) -> tuple[ActiveVKUserDTO, ...]:
        async with self._session_pool() as session:
            return await UserRepository(session=session).list_active_users_page(
                after_users_id=after_users_id,
                limit=limit,
            )
