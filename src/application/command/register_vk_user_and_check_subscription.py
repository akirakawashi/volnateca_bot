from dataclasses import dataclass

from application.base_interactor import Interactor
from application.command.complete_vk_subscription_task import (
    CompleteVKSubscriptionTaskCommand,
    CompleteVKSubscriptionTaskHandler,
)
from application.command.register_vk_user import RegisterVKUserCommand, RegisterVKUserHandler
from application.common.dto.task import VKSubscriptionTaskCompletionDTO
from application.common.dto.user import VKUserRegistrationDTO


@dataclass(slots=True, frozen=True, kw_only=True)
class RegisterVKUserAndCheckSubscriptionCommand:
    event_id: str | None
    vk_user_id: int
    first_name: str | None = None
    last_name: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class RegisterVKUserAndCheckSubscriptionDTO:
    registration: VKUserRegistrationDTO
    subscription: VKSubscriptionTaskCompletionDTO


class RegisterVKUserAndCheckSubscriptionHandler(
    Interactor[
        RegisterVKUserAndCheckSubscriptionCommand,
        RegisterVKUserAndCheckSubscriptionDTO,
    ],
):
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
