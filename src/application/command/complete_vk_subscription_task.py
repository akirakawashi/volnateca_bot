from dataclasses import dataclass

from loguru import logger

from application.base_interactor import Interactor
from application.common.dto.task import (
    VKSubscriptionTaskCompletionDTO,
    VKSubscriptionTaskCompletionStatus,
)
from application.interface.clients import IVKUserClient
from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.tasks import ITaskRepository
from application.interface.uow import IUnitOfWork
from application.services.award_task_service import (
    AwardTaskOutcome,
    AwardTaskOutcomeStatus,
    AwardTaskService,
    TaskAwardSpec,
)
from application.services.vk_subscription_task_rules import VKSubscriptionTaskRules
from domain.enums.task import TaskRepeatPolicy


@dataclass(slots=True, frozen=True, kw_only=True)
class CompleteVKSubscriptionTaskCommand:
    event_id: str | None
    vk_user_id: int


class CompleteVKSubscriptionTaskHandler(
    Interactor[CompleteVKSubscriptionTaskCommand, VKSubscriptionTaskCompletionDTO],
):
    def __init__(
        self,
        task_repository: ITaskRepository,
        task_completion_repository: ITaskCompletionRepository,
        award_service: AwardTaskService,
        uow: IUnitOfWork,
        vk_user_client: IVKUserClient,
        required_subscription_group_id: int,
        subscription_task_rules: VKSubscriptionTaskRules | None = None,
    ) -> None:
        self.task_repository = task_repository
        self.task_completion_repository = task_completion_repository
        self.award_service = award_service
        self.uow = uow
        self.vk_user_client = vk_user_client
        self.required_subscription_group_id = required_subscription_group_id
        self.subscription_task_rules = subscription_task_rules or VKSubscriptionTaskRules()

    async def __call__(
        self,
        command_data: CompleteVKSubscriptionTaskCommand,
    ) -> VKSubscriptionTaskCompletionDTO:
        task = await self.task_repository.get_or_create_subscription_task(
            code=self._build_task_code(group_id=self.required_subscription_group_id),
            task_name="Подписаться на группу Волны",
            description="Бонус за подписку на группу Волны ВКонтакте.",
            external_id=self._build_task_external_id(group_id=self.required_subscription_group_id),
            points=self.subscription_task_rules.points,
            week_number=self.subscription_task_rules.week_number,
            repeat_policy=TaskRepeatPolicy.ONCE,
        )

        if await self.task_completion_repository.is_completed_by_vk_user(
            vk_user_id=command_data.vk_user_id,
            tasks_id=task.tasks_id,
            completion_key=self.subscription_task_rules.completion_key,
        ):
            return VKSubscriptionTaskCompletionDTO(
                status=VKSubscriptionTaskCompletionStatus.ALREADY_COMPLETED,
                vk_user_id=command_data.vk_user_id,
                tasks_id=task.tasks_id,
            )

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

        spec = TaskAwardSpec(
            tasks_id=task.tasks_id,
            task_name=task.task_name,
            points=task.points,
        )
        if not is_member:
            outcome = await self.award_service.reject(
                vk_user_id=command_data.vk_user_id,
                task=spec,
                completion_key=self.subscription_task_rules.completion_key,
                event_id=command_data.event_id,
                evidence_external_id=task.external_id,
                rejected_reason=self.subscription_task_rules.rejected_reason,
            )
        else:
            outcome = await self.award_service.award(
                vk_user_id=command_data.vk_user_id,
                task=spec,
                completion_key=self.subscription_task_rules.completion_key,
                event_id=command_data.event_id,
                evidence_external_id=task.external_id,
            )

        await self.uow.commit()
        return self._to_completion_dto(outcome=outcome)

    @staticmethod
    def _to_completion_dto(outcome: AwardTaskOutcome) -> VKSubscriptionTaskCompletionDTO:
        return VKSubscriptionTaskCompletionDTO(
            status=_map_status(outcome=outcome.status),
            vk_user_id=outcome.vk_user_id,
            users_id=outcome.users_id,
            tasks_id=outcome.tasks_id,
            task_completions_id=outcome.task_completions_id,
            transactions_id=outcome.transactions_id,
            points_awarded=outcome.points_awarded,
            balance_points=outcome.balance_points,
            rejected_reason=outcome.rejected_reason,
        )

    @staticmethod
    def _build_task_code(group_id: int) -> str:
        return f"vk_subscribe_group_{abs(group_id)}"

    @staticmethod
    def _build_task_external_id(group_id: int) -> str:
        return f"group{abs(group_id)}"


def _map_status(outcome: AwardTaskOutcomeStatus) -> VKSubscriptionTaskCompletionStatus:
    match outcome:
        case AwardTaskOutcomeStatus.COMPLETED:
            return VKSubscriptionTaskCompletionStatus.COMPLETED
        case AwardTaskOutcomeStatus.ALREADY_COMPLETED:
            return VKSubscriptionTaskCompletionStatus.ALREADY_COMPLETED
        case AwardTaskOutcomeStatus.REJECTED:
            return VKSubscriptionTaskCompletionStatus.REJECTED
        case AwardTaskOutcomeStatus.USER_NOT_REGISTERED:
            return VKSubscriptionTaskCompletionStatus.USER_NOT_REGISTERED
