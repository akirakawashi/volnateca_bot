from dataclasses import dataclass, replace

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
      - если пользователя нет, обработчик сначала атомарно создаёт
        запись с регистрационным бонусом, а затем best-effort
        дозаполняет профиль из VK без влияния на успешную регистрацию.

    Такое поведение убирает лишние вызовы VK API на повторных и
    конкурентных callback-ах и не держит DB-соединение во время
    внешнего запроса.
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
            return existing_user

        user = await self.repository.create_registered_user(
            vk_user_id=command_data.vk_user_id,
            first_name=command_data.first_name,
            last_name=command_data.last_name,
            vk_screen_name=None,
            bonus_points=REGISTRATION_BONUS_POINTS,
        )
        await self.uow.commit()
        if not user.created:
            return user

        return await self._enrich_profile_after_registration(
            command_data=command_data,
            registration=user,
        )

    async def _enrich_profile_after_registration(
        self,
        *,
        command_data: RegisterVKUserCommand,
        registration: VKUserRegistrationDTO,
    ) -> VKUserRegistrationDTO:
        try:
            profile = await self.vk_user_client.get_user_profile(
                vk_user_id=command_data.vk_user_id,
            )
            if profile is None:
                return registration

            await self.repository.update_vk_profile(
                vk_user_id=command_data.vk_user_id,
                first_name=profile.first_name,
                last_name=profile.last_name,
                vk_screen_name=profile.screen_name,
            )
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            return registration

        return replace(
            registration,
            vk_screen_name=profile.screen_name,
        )
