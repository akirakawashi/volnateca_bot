from dataclasses import dataclass

from loguru import logger

from application.base_interactor import Interactor
from application.common.dto.task import (
    VKSubscriptionTaskCompletionDTO,
    VKSubscriptionTaskCompletionStatus,
)
from application.interface.clients import IVKUserClient
from application.interface.repositories.tasks import ITaskCompletionRepository
from application.interface.uow import IUnitOfWork
from domain.enums.task import TaskRepeatPolicy

SUBSCRIPTION_TASK_POINTS = 15
SUBSCRIPTION_TASK_WEEK_NUMBER = 1
SUBSCRIPTION_TASK_COMPLETION_KEY = "once"
SUBSCRIPTION_REJECTED_REASON = "vk_user_is_not_group_member"


@dataclass(slots=True, frozen=True, kw_only=True)
class CompleteVKSubscriptionTaskCommand:
    event_id: str | None
    vk_user_id: int


class CompleteVKSubscriptionTaskHandler(
    Interactor[CompleteVKSubscriptionTaskCommand, VKSubscriptionTaskCompletionDTO],
):
    def __init__(
        self,
        repository: ITaskCompletionRepository,
        uow: IUnitOfWork,
        vk_user_client: IVKUserClient,
        required_subscription_group_id: int,
    ) -> None:
        self.repository = repository
        self.uow = uow
        self.vk_user_client = vk_user_client
        self.required_subscription_group_id = required_subscription_group_id

    async def __call__(
        self,
        command_data: CompleteVKSubscriptionTaskCommand,
    ) -> VKSubscriptionTaskCompletionDTO:
        is_member = await self.vk_user_client.is_group_member(
            vk_user_id=command_data.vk_user_id,
            group_id=self.required_subscription_group_id,
        )
        if is_member is None:
            logger.warning(
                "VK subscription task check unavailable: event_id={}, vk_user_id={}, group_id={}",
                command_data.event_id,
                command_data.vk_user_id,
                self.required_subscription_group_id,
            )
            return VKSubscriptionTaskCompletionDTO(
                status=VKSubscriptionTaskCompletionStatus.VK_API_UNAVAILABLE,
                vk_user_id=command_data.vk_user_id,
            )

        task = await self.repository.get_or_create_subscription_task(
            code=self._build_task_code(group_id=self.required_subscription_group_id),
            task_name="Подписаться на группу Волны",
            description="Бонус за подписку на группу Волны ВКонтакте.",
            external_id=self._build_task_external_id(group_id=self.required_subscription_group_id),
            points=SUBSCRIPTION_TASK_POINTS,
            week_number=SUBSCRIPTION_TASK_WEEK_NUMBER,
            repeat_policy=TaskRepeatPolicy.ONCE,
        )

        if not is_member:
            result = await self.repository.reject_subscription_task_for_vk_user(
                vk_user_id=command_data.vk_user_id,
                task=task,
                completion_key=SUBSCRIPTION_TASK_COMPLETION_KEY,
                event_id=command_data.event_id,
                evidence_external_id=task.external_id,
                rejected_reason=SUBSCRIPTION_REJECTED_REASON,
            )
            await self.uow.commit()
            return result

        result = await self.repository.complete_subscription_task_for_vk_user(
            vk_user_id=command_data.vk_user_id,
            task=task,
            completion_key=SUBSCRIPTION_TASK_COMPLETION_KEY,
            event_id=command_data.event_id,
            evidence_external_id=task.external_id,
        )
        await self.uow.commit()
        return result

    @staticmethod
    def _build_task_code(group_id: int) -> str:
        return f"vk_subscribe_group_{abs(group_id)}"

    @staticmethod
    def _build_task_external_id(group_id: int) -> str:
        return f"group{abs(group_id)}"
