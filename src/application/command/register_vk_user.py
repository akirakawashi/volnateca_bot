from dataclasses import dataclass

from application.base_interactor import Interactor
from application.common.dto.user import VKUserRegistrationDTO
from application.interface.repositories.users import IUserRepository
from application.interface.uow import IUnitOfWork

REGISTRATION_BONUS_POINTS = 15


@dataclass(slots=True, frozen=True, kw_only=True)
class RegisterVKUserCommand:
    vk_user_id: int
    first_name: str | None = None
    last_name: str | None = None


class RegisterVKUserHandler(Interactor[RegisterVKUserCommand, VKUserRegistrationDTO]):
    def __init__(
        self,
        repository: IUserRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.repository = repository
        self.uow = uow

    async def __call__(
        self,
        command_data: RegisterVKUserCommand,
    ) -> VKUserRegistrationDTO:
        user = await self.repository.get_by_vk_user_id(
            vk_user_id=command_data.vk_user_id,
        )
        if user is not None:
            user = await self.repository.update_profile(
                users_id=user.users_id,
                first_name=command_data.first_name,
                last_name=command_data.last_name,
            )
            await self.uow.commit()
            return user

        user = await self.repository.create_registered_user(
            vk_user_id=command_data.vk_user_id,
            first_name=command_data.first_name,
            last_name=command_data.last_name,
            bonus_points=REGISTRATION_BONUS_POINTS,
        )
        await self.uow.commit()
        return user
