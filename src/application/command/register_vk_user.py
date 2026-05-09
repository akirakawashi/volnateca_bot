from dataclasses import dataclass

from loguru import logger

from application.base_interactor import Interactor
from application.common.dto.user import VKUserRegistrationDTO
from application.interface.clients import IVKUserClient
from application.interface.repositories.users import IUserRepository
from application.interface.uow import IUnitOfWork

REGISTRATION_BONUS_POINTS = 15


@dataclass(slots=True, frozen=True, kw_only=True)
class RegisterVKUserCommand:
    vk_user_id: int
    first_name: str | None = None
    last_name: str | None = None


class RegisterVKUserHandler(Interactor[RegisterVKUserCommand, VKUserRegistrationDTO]):
    """Регистрирует пользователя VK один раз.

    Контракт:
      - если пользователь уже существует, обработчик НЕ дергает VK API
        и НЕ обновляет профиль/баланс. Возвращает DTO с created=False.
        Никакой commit при этом не выполняется.
      - если пользователя нет, обработчик подтягивает профиль из VK и
        создаёт запись с регистрационным бонусом, после чего коммитит.

    Такое поведение убирает лишние вызовы VK API и обновления профиля
    на каждое входящее сообщение и страхует от двойного commit'а в
    композитных сценариях.
    """

    def __init__(
        self,
        repository: IUserRepository,
        uow: IUnitOfWork,
        vk_user_client: IVKUserClient,
    ) -> None:
        self.repository = repository
        self.uow = uow
        self.vk_user_client = vk_user_client

    async def __call__(
        self,
        command_data: RegisterVKUserCommand,
    ) -> VKUserRegistrationDTO:
        existing_user = await self.repository.get_by_vk_user_id(
            vk_user_id=command_data.vk_user_id,
        )
        if existing_user is not None:
            logger.info(
                "TEMP VK user already registered, skipping VK API and DB writes: "
                "vk_user_id={}, users_id={}, screen_name={}",
                command_data.vk_user_id,
                existing_user.users_id,
                existing_user.vk_screen_name,
            )
            return existing_user

        profile = await self.vk_user_client.get_user_profile(vk_user_id=command_data.vk_user_id)
        first_name = self._select_profile_value(
            profile_value=profile.first_name if profile else None,
            fallback_value=command_data.first_name,
        )
        last_name = self._select_profile_value(
            profile_value=profile.last_name if profile else None,
            fallback_value=command_data.last_name,
        )
        vk_screen_name = profile.screen_name if profile else None

        user = await self.repository.create_registered_user(
            vk_user_id=command_data.vk_user_id,
            first_name=first_name,
            last_name=last_name,
            vk_screen_name=vk_screen_name,
            bonus_points=REGISTRATION_BONUS_POINTS,
        )
        await self.uow.commit()
        logger.info(
            "TEMP VK user registered: vk_user_id={}, users_id={}, screen_name={}, bonus_points={}",
            command_data.vk_user_id,
            user.users_id,
            user.vk_screen_name,
            REGISTRATION_BONUS_POINTS,
        )
        return user

    @staticmethod
    def _select_profile_value(
        profile_value: str | None,
        fallback_value: str | None,
    ) -> str | None:
        return profile_value if profile_value is not None else fallback_value
