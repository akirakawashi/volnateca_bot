from abc import ABC, abstractmethod

from application.common.dto.user import ActiveVKUserDTO


class IBroadcastRecipientReader(ABC):
    @abstractmethod
    async def count_active_users(self) -> int:
        raise NotImplementedError

    @abstractmethod
    async def list_active_users_page(
        self,
        *,
        after_users_id: int | None,
        limit: int,
    ) -> tuple[ActiveVKUserDTO, ...]:
        raise NotImplementedError
