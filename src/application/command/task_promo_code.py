from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from application.base_interactor import Interactor
from application.common.dto.task import TaskCompletionResult
from application.common.dto.task_promo_code import normalize_task_promo_code
from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.task_promo_code_waits import ITaskPromoCodeWaitRepository
from application.interface.repositories.task_promo_codes import ITaskPromoCodeRepository
from application.interface.repositories.tasks import ITaskRepository
from application.interface.repositories.users import IUserRepository
from application.interface.uow import IUnitOfWork
from application.services.award_task_service import AwardTaskService, TaskAwardSpec
from application.services.task_completion_key import build_task_completion_key
from application.services.task_completion_result import build_task_completion_result
from domain.enums.task import TaskType


class TaskPromoCodeFlowStatus(str, Enum):
    STARTED = "started"
    CANCELED = "canceled"
    NO_ACTIVE_WAIT = "no_active_wait"
    INVALID_CODE = "invalid_code"
    COMPLETED = "completed"
    ALREADY_COMPLETED = "already_completed"
    TASK_NOT_FOUND = "task_not_found"
    USER_NOT_REGISTERED = "user_not_registered"


@dataclass(slots=True, frozen=True, kw_only=True)
class StartTaskPromoCodeCommand:
    vk_user_id: int
    tasks_id: int


@dataclass(slots=True, frozen=True, kw_only=True)
class ActivateTaskPromoCodeCommand:
    event_id: str | None
    vk_user_id: int
    promo_code: str


@dataclass(slots=True, frozen=True, kw_only=True)
class CancelTaskPromoCodeCommand:
    vk_user_id: int


@dataclass(slots=True, frozen=True, kw_only=True)
class GetTaskPromoCodeWaitCommand:
    vk_user_id: int


@dataclass(slots=True, frozen=True, kw_only=True)
class TaskPromoCodeFlowDTO:
    status: TaskPromoCodeFlowStatus
    vk_user_id: int
    users_id: int | None = None
    tasks_id: int | None = None
    task_name: str | None = None
    points: int | None = None
    image_attachment: str | None = None
    completion: TaskCompletionResult | None = None


class StartTaskPromoCodeHandler(
    Interactor[StartTaskPromoCodeCommand, TaskPromoCodeFlowDTO],
):
    def __init__(
        self,
        user_repository: IUserRepository,
        task_repository: ITaskRepository,
        wait_repository: ITaskPromoCodeWaitRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.user_repository = user_repository
        self.task_repository = task_repository
        self.wait_repository = wait_repository
        self.uow = uow

    async def __call__(self, command_data: StartTaskPromoCodeCommand) -> TaskPromoCodeFlowDTO:
        user = await self.user_repository.get_by_vk_user_id(vk_user_id=command_data.vk_user_id)
        if user is None:
            return TaskPromoCodeFlowDTO(
                status=TaskPromoCodeFlowStatus.USER_NOT_REGISTERED,
                vk_user_id=command_data.vk_user_id,
            )

        tasks = await self.task_repository.list_available_tasks_for_vk_user(
            vk_user_id=command_data.vk_user_id,
        )
        task = next(
            (
                item
                for item in tasks
                if item.tasks_id == command_data.tasks_id and item.task_type == TaskType.CUSTOM
            ),
            None,
        )
        if task is None:
            return TaskPromoCodeFlowDTO(
                status=TaskPromoCodeFlowStatus.TASK_NOT_FOUND,
                vk_user_id=command_data.vk_user_id,
                users_id=user.users_id,
                tasks_id=command_data.tasks_id,
            )

        await self.wait_repository.start_waiting(
            users_id=user.users_id,
            tasks_id=task.tasks_id,
        )
        await self.uow.commit()
        return TaskPromoCodeFlowDTO(
            status=TaskPromoCodeFlowStatus.STARTED,
            vk_user_id=command_data.vk_user_id,
            users_id=user.users_id,
            tasks_id=task.tasks_id,
            task_name=task.task_name,
            points=task.points,
            image_attachment=task.image_attachment,
        )


class ActivateTaskPromoCodeHandler(
    Interactor[ActivateTaskPromoCodeCommand, TaskPromoCodeFlowDTO],
):
    def __init__(
        self,
        user_repository: IUserRepository,
        task_repository: ITaskRepository,
        task_completion_repository: ITaskCompletionRepository,
        promo_code_repository: ITaskPromoCodeRepository,
        wait_repository: ITaskPromoCodeWaitRepository,
        award_service: AwardTaskService,
        uow: IUnitOfWork,
    ) -> None:
        self.user_repository = user_repository
        self.task_repository = task_repository
        self.task_completion_repository = task_completion_repository
        self.promo_code_repository = promo_code_repository
        self.wait_repository = wait_repository
        self.award_service = award_service
        self.uow = uow

    async def __call__(self, command_data: ActivateTaskPromoCodeCommand) -> TaskPromoCodeFlowDTO:
        user = await self.user_repository.get_by_vk_user_id(vk_user_id=command_data.vk_user_id)
        if user is None:
            return TaskPromoCodeFlowDTO(
                status=TaskPromoCodeFlowStatus.USER_NOT_REGISTERED,
                vk_user_id=command_data.vk_user_id,
            )

        wait = await self.wait_repository.get_waiting_for_update(users_id=user.users_id)
        if wait is None:
            return TaskPromoCodeFlowDTO(
                status=TaskPromoCodeFlowStatus.NO_ACTIVE_WAIT,
                vk_user_id=command_data.vk_user_id,
                users_id=user.users_id,
            )

        task = await self.task_repository.get_task_for_award_for_update(tasks_id=wait.tasks_id)
        if task is None:
            await self.wait_repository.cancel_waiting(
                task_promo_code_waits_id=wait.task_promo_code_waits_id,
            )
            await self.uow.commit()
            return TaskPromoCodeFlowDTO(
                status=TaskPromoCodeFlowStatus.TASK_NOT_FOUND,
                vk_user_id=command_data.vk_user_id,
                users_id=user.users_id,
                tasks_id=wait.tasks_id,
            )

        completion_key = build_task_completion_key(
            repeat_policy=task.repeat_policy,
            week_number=task.week_number,
            checked_at=datetime.now(tz=UTC),
        )
        if await self.task_completion_repository.is_completed_by_vk_user(
            vk_user_id=command_data.vk_user_id,
            tasks_id=task.tasks_id,
            completion_key=completion_key,
        ):
            await self.wait_repository.complete_waiting(
                task_promo_code_waits_id=wait.task_promo_code_waits_id,
            )
            await self.uow.commit()
            return TaskPromoCodeFlowDTO(
                status=TaskPromoCodeFlowStatus.ALREADY_COMPLETED,
                vk_user_id=command_data.vk_user_id,
                users_id=user.users_id,
                tasks_id=task.tasks_id,
                task_name=task.task_name,
                points=task.points,
            )

        normalized_code = normalize_task_promo_code(command_data.promo_code)
        code = await self.promo_code_repository.get_by_task_for_update(tasks_id=task.tasks_id)
        if code is None:
            await self.wait_repository.cancel_waiting(
                task_promo_code_waits_id=wait.task_promo_code_waits_id,
            )
            await self.uow.commit()
            return TaskPromoCodeFlowDTO(
                status=TaskPromoCodeFlowStatus.TASK_NOT_FOUND,
                vk_user_id=command_data.vk_user_id,
                users_id=user.users_id,
                tasks_id=task.tasks_id,
                task_name=task.task_name,
                points=task.points,
            )
        if code.promo_code != normalized_code:
            await self.uow.commit()
            return TaskPromoCodeFlowDTO(
                status=TaskPromoCodeFlowStatus.INVALID_CODE,
                vk_user_id=command_data.vk_user_id,
                users_id=user.users_id,
                tasks_id=task.tasks_id,
                task_name=task.task_name,
                points=task.points,
            )

        outcome = await self.award_service.award(
            vk_user_id=command_data.vk_user_id,
            task=TaskAwardSpec(
                tasks_id=task.tasks_id,
                task_name=task.task_name,
                points=task.points,
                week_number=task.week_number,
            ),
            completion_key=completion_key,
            event_id=command_data.event_id,
            evidence_external_id=code.promo_code,
        )
        completion = build_task_completion_result(outcome=outcome)
        await self.wait_repository.complete_waiting(
            task_promo_code_waits_id=wait.task_promo_code_waits_id,
        )
        await self.uow.commit()

        return TaskPromoCodeFlowDTO(
            status=TaskPromoCodeFlowStatus(completion.status.value),
            vk_user_id=command_data.vk_user_id,
            users_id=user.users_id,
            tasks_id=task.tasks_id,
            task_name=task.task_name,
            points=task.points,
            completion=completion,
        )


class CancelTaskPromoCodeHandler(
    Interactor[CancelTaskPromoCodeCommand, TaskPromoCodeFlowDTO],
):
    def __init__(
        self,
        user_repository: IUserRepository,
        wait_repository: ITaskPromoCodeWaitRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.user_repository = user_repository
        self.wait_repository = wait_repository
        self.uow = uow

    async def __call__(self, command_data: CancelTaskPromoCodeCommand) -> TaskPromoCodeFlowDTO:
        user = await self.user_repository.get_by_vk_user_id(vk_user_id=command_data.vk_user_id)
        if user is None:
            return TaskPromoCodeFlowDTO(
                status=TaskPromoCodeFlowStatus.USER_NOT_REGISTERED,
                vk_user_id=command_data.vk_user_id,
            )

        wait = await self.wait_repository.get_waiting_for_update(users_id=user.users_id)
        if wait is None:
            return TaskPromoCodeFlowDTO(
                status=TaskPromoCodeFlowStatus.NO_ACTIVE_WAIT,
                vk_user_id=command_data.vk_user_id,
                users_id=user.users_id,
            )

        await self.wait_repository.cancel_waiting(
            task_promo_code_waits_id=wait.task_promo_code_waits_id,
        )
        await self.uow.commit()
        return TaskPromoCodeFlowDTO(
            status=TaskPromoCodeFlowStatus.CANCELED,
            vk_user_id=command_data.vk_user_id,
            users_id=user.users_id,
            tasks_id=wait.tasks_id,
        )


class GetTaskPromoCodeWaitHandler(
    Interactor[GetTaskPromoCodeWaitCommand, TaskPromoCodeFlowDTO],
):
    def __init__(
        self,
        user_repository: IUserRepository,
        wait_repository: ITaskPromoCodeWaitRepository,
    ) -> None:
        self.user_repository = user_repository
        self.wait_repository = wait_repository

    async def __call__(self, command_data: GetTaskPromoCodeWaitCommand) -> TaskPromoCodeFlowDTO:
        user = await self.user_repository.get_by_vk_user_id(vk_user_id=command_data.vk_user_id)
        if user is None:
            return TaskPromoCodeFlowDTO(
                status=TaskPromoCodeFlowStatus.USER_NOT_REGISTERED,
                vk_user_id=command_data.vk_user_id,
            )

        wait = await self.wait_repository.get_waiting(users_id=user.users_id)
        if wait is None:
            return TaskPromoCodeFlowDTO(
                status=TaskPromoCodeFlowStatus.NO_ACTIVE_WAIT,
                vk_user_id=command_data.vk_user_id,
                users_id=user.users_id,
            )

        return TaskPromoCodeFlowDTO(
            status=TaskPromoCodeFlowStatus.STARTED,
            vk_user_id=command_data.vk_user_id,
            users_id=user.users_id,
            tasks_id=wait.tasks_id,
        )
