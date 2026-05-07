from abc import ABC, abstractmethod

from application.common.dto.vk import VKUserProfileDTO, VKWallPostDTO


class IVKUserClient(ABC):
    @abstractmethod
    async def get_user_profile(self, vk_user_id: int) -> VKUserProfileDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def is_group_member(self, vk_user_id: int, group_id: int) -> bool | None:
        raise NotImplementedError

    @abstractmethod
    async def has_user_reposted_wall_post(
        self,
        vk_user_id: int,
        post: VKWallPostDTO,
    ) -> bool | None:
        raise NotImplementedError
