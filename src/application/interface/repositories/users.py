from abc import ABC, abstractmethod

from application.common.dto.user import VKUserRegistrationDTO


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_vk_user_id(
        self,
        vk_user_id: int,
    ) -> VKUserRegistrationDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def create_registered_user(
        self,
        vk_user_id: int,
        first_name: str | None,
        last_name: str | None,
        bonus_points: int,
    ) -> VKUserRegistrationDTO:
        raise NotImplementedError

    @abstractmethod
    async def update_profile(
        self,
        users_id: int,
        first_name: str | None,
        last_name: str | None,
    ) -> VKUserRegistrationDTO:
        raise NotImplementedError
