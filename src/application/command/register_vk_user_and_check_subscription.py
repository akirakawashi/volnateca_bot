from dataclasses import dataclass

from application.base_interactor import Interactor
from application.command.complete_vk_subscription_task import (
    CompleteVKSubscriptionTaskCommand,
    CompleteVKSubscriptionTaskHandler,
)
from application.command.register_vk_user import RegisterVKUserCommand, RegisterVKUserHandler
from application.common.dto.task import TaskCompletionResult
from application.common.dto.user import VKUserRegistrationDTO


@dataclass(slots=True, frozen=True, kw_only=True)
class RegisterVKUserAndCheckSubscriptionCommand:
    event_id: str | None
    vk_user_id: int
    first_name: str | None = None
    last_name: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class RegisterVKUserAndCheckSubscriptionDTO:
    """Результат сценария «зашёл по сообщению».

    `subscription` равен None, если пользователь уже был зарегистрирован
    ранее: в этом случае страховочная проверка подписки не запускается,
    бонус за подписку начисляется только через GROUP_JOIN.
    """

    registration: VKUserRegistrationDTO
    subscription: TaskCompletionResult | None


class RegisterVKUserAndCheckSubscriptionHandler(
    Interactor[
        RegisterVKUserAndCheckSubscriptionCommand,
        RegisterVKUserAndCheckSubscriptionDTO,
    ],
):
    """Сценарий первого сообщения боту.

    Если пользователь уже зарегистрирован — никакой работы: ни записей в БД,
    ни обращений к VK API. Это предотвращает дёргание VK на каждое входящее
    сообщение и снимает риск «двойного commit'а» из-за повторного запуска
    проверки подписки.

    Если пользователь новый — регистрируем и сразу делаем разовую
    страховочную проверку подписки (на случай, если он уже был в группе
    до первого сообщения).
    """

    def __init__(
        self,
        register_vk_user_interactor: RegisterVKUserHandler,
        complete_vk_subscription_task_interactor: CompleteVKSubscriptionTaskHandler,
    ) -> None:
        self.register_vk_user_interactor = register_vk_user_interactor
        self.complete_vk_subscription_task_interactor = complete_vk_subscription_task_interactor

    async def __call__(
        self,
        command_data: RegisterVKUserAndCheckSubscriptionCommand,
    ) -> RegisterVKUserAndCheckSubscriptionDTO:
        registration = await self.register_vk_user_interactor(
            command_data=RegisterVKUserCommand(
                vk_user_id=command_data.vk_user_id,
                first_name=command_data.first_name,
                last_name=command_data.last_name,
            ),
        )
        if not registration.created:
            return RegisterVKUserAndCheckSubscriptionDTO(
                registration=registration,
                subscription=None,
            )

        subscription = await self.complete_vk_subscription_task_interactor(
            command_data=CompleteVKSubscriptionTaskCommand(
                event_id=command_data.event_id,
                vk_user_id=command_data.vk_user_id,
            ),
        )
        return RegisterVKUserAndCheckSubscriptionDTO(
            registration=registration,
            subscription=subscription,
        )
