from abc import ABC, abstractmethod

from application.admin.dto.user import (
    UserProfileAdminDTO,
    UserReferralsAdminDTO,
    UserSearchHitDTO,
)


class IUserAdminRepository(ABC):
    @abstractmethod
    async def search(self, *, query: str, limit: int) -> tuple[UserSearchHitDTO, ...]:
        raise NotImplementedError

    @abstractmethod
    async def get_profile(self, *, users_id: int) -> UserProfileAdminDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, *, users_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def list_referrals_for_user(self, *, users_id: int) -> UserReferralsAdminDTO:
        raise NotImplementedError


__all__ = ["IUserAdminRepository"]
