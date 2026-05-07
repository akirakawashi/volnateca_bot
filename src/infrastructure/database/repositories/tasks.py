from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlmodel import col

from application.common.dto.task import (
    VKRepostTaskCompletionDTO,
    VKRepostTaskCreationDTO,
    VKRepostTaskCreationStatus,
    VKRepostTaskCompletionStatus,
    VKRepostTaskDTO,
)
from application.interface.repositories.tasks import ITaskCompletionRepository
from domain.enums.task import TaskCompletionStatus, TaskRepeatPolicy, TaskType
from domain.enums.transaction import TransactionSource, TransactionType
from infrastructure.database.models.task_completions import TaskCompletion
from infrastructure.database.models.tasks import Task
from infrastructure.database.models.transactions import Transaction
from infrastructure.database.models.users import User
from infrastructure.database.repositories.base import SQLAlchemyRepository


class TaskCompletionRepository(SQLAlchemyRepository, ITaskCompletionRepository):
    async def create_repost_task_if_not_exists(
        self,
        code: str,
        task_name: str,
        description: str,
        external_id: str,
        points: int,
        week_number: int | None,
        repeat_policy: TaskRepeatPolicy,
        event_id: str | None,
    ) -> VKRepostTaskCreationDTO:
        existing_task = await self._get_repost_task_by_code_or_external_id(
            code=code,
            external_id=external_id,
        )
        if existing_task is not None:
            return self._to_repost_task_creation_dto(
                status=VKRepostTaskCreationStatus.ALREADY_EXISTS,
                task=existing_task,
                event_id=event_id,
            )

        task = Task(
            code=code,
            task_name=task_name,
            description=description,
            task_type=TaskType.VK_REPOST,
            points=points,
            week_number=week_number,
            external_id=external_id,
            repeat_policy=repeat_policy,
            is_active=True,
        )
        self._session.add(task)
        await self._session.flush()
        return self._to_repost_task_creation_dto(
            status=VKRepostTaskCreationStatus.CREATED,
            task=task,
            event_id=event_id,
        )

    async def get_active_repost_task_by_external_ids(
        self,
        external_ids: tuple[str, ...],
    ) -> VKRepostTaskDTO | None:
        if not external_ids:
            return None

        now = datetime.now(tz=UTC)
        result = await self._session.execute(
            select(Task)
            .where(
                col(Task.task_type) == TaskType.VK_REPOST,
                col(Task.external_id).in_(external_ids),
                col(Task.is_active).is_(True),
                or_(col(Task.starts_at).is_(None), col(Task.starts_at) <= now),
                or_(col(Task.ends_at).is_(None), col(Task.ends_at) > now),
            )
            .order_by(col(Task.tasks_id)),
        )
        task = result.scalars().first()
        if task is None:
            return None

        return self._to_repost_task_dto(task=task)

    async def complete_repost_task_for_vk_user(
        self,
        vk_user_id: int,
        task: VKRepostTaskDTO,
        completion_key: str,
        event_id: str | None,
        evidence_external_id: str | None,
    ) -> VKRepostTaskCompletionDTO:
        user = await self._get_user_for_update(vk_user_id=vk_user_id)
        if user is None:
            return VKRepostTaskCompletionDTO(
                status=VKRepostTaskCompletionStatus.USER_NOT_REGISTERED,
                vk_user_id=vk_user_id,
                tasks_id=task.tasks_id,
            )

        completion = await self._get_completion_for_update(
            users_id=self._require_user_id(user=user),
            tasks_id=task.tasks_id,
            completion_key=completion_key,
        )
        if completion and completion.task_completion_status == TaskCompletionStatus.COMPLETED:
            return self._to_completion_result(
                status=VKRepostTaskCompletionStatus.ALREADY_COMPLETED,
                vk_user_id=vk_user_id,
                user=user,
                completion=completion,
                points_awarded=0,
            )

        balance_before = user.balance_points
        balance_after = balance_before + task.points
        user.balance_points = balance_after
        user.earned_points_total += task.points

        transaction = Transaction(
            users_id=self._require_user_id(user=user),
            tasks_id=task.tasks_id,
            transaction_type=TransactionType.ACCRUAL,
            transaction_source=TransactionSource.TASK,
            amount=task.points,
            balance_before=balance_before,
            balance_after=balance_after,
            description=f"Начисление за задание: {task.task_name}",
        )
        self._session.add(transaction)
        await self._session.flush()
        if transaction.transactions_id is None:
            raise RuntimeError("Transaction primary key was not generated")

        now = datetime.now(tz=UTC)
        if completion is None:
            completion = TaskCompletion(
                users_id=self._require_user_id(user=user),
                tasks_id=task.tasks_id,
                completion_key=completion_key,
                transactions_id=transaction.transactions_id,
                task_completion_status=TaskCompletionStatus.COMPLETED,
                points_awarded=task.points,
                external_event_id=event_id,
                evidence_external_id=evidence_external_id,
                checked_at=now,
            )
            self._session.add(completion)
        else:
            completion.transactions_id = transaction.transactions_id
            completion.task_completion_status = TaskCompletionStatus.COMPLETED
            completion.points_awarded = task.points
            completion.external_event_id = event_id
            completion.evidence_external_id = evidence_external_id
            completion.rejected_reason = None
            completion.checked_at = now

        await self._session.flush()
        return self._to_completion_result(
            status=VKRepostTaskCompletionStatus.COMPLETED,
            vk_user_id=vk_user_id,
            user=user,
            completion=completion,
            points_awarded=task.points,
        )

    async def reject_repost_task_for_vk_user(
        self,
        vk_user_id: int,
        task: VKRepostTaskDTO,
        completion_key: str,
        event_id: str | None,
        evidence_external_id: str | None,
        rejected_reason: str,
    ) -> VKRepostTaskCompletionDTO:
        user = await self._get_user_for_update(vk_user_id=vk_user_id)
        if user is None:
            return VKRepostTaskCompletionDTO(
                status=VKRepostTaskCompletionStatus.USER_NOT_REGISTERED,
                vk_user_id=vk_user_id,
                tasks_id=task.tasks_id,
                rejected_reason=rejected_reason,
            )

        completion = await self._get_completion_for_update(
            users_id=self._require_user_id(user=user),
            tasks_id=task.tasks_id,
            completion_key=completion_key,
        )
        if completion and completion.task_completion_status == TaskCompletionStatus.COMPLETED:
            return self._to_completion_result(
                status=VKRepostTaskCompletionStatus.ALREADY_COMPLETED,
                vk_user_id=vk_user_id,
                user=user,
                completion=completion,
                points_awarded=0,
            )

        now = datetime.now(tz=UTC)
        if completion is None:
            completion = TaskCompletion(
                users_id=self._require_user_id(user=user),
                tasks_id=task.tasks_id,
                completion_key=completion_key,
                task_completion_status=TaskCompletionStatus.REJECTED,
                points_awarded=0,
                external_event_id=event_id,
                evidence_external_id=evidence_external_id,
                rejected_reason=rejected_reason,
                checked_at=now,
            )
            self._session.add(completion)
        else:
            completion.task_completion_status = TaskCompletionStatus.REJECTED
            completion.points_awarded = 0
            completion.external_event_id = event_id
            completion.evidence_external_id = evidence_external_id
            completion.rejected_reason = rejected_reason
            completion.checked_at = now

        await self._session.flush()
        return self._to_completion_result(
            status=VKRepostTaskCompletionStatus.REJECTED,
            vk_user_id=vk_user_id,
            user=user,
            completion=completion,
            points_awarded=0,
            rejected_reason=rejected_reason,
        )

    async def _get_user_for_update(self, vk_user_id: int) -> User | None:
        result = await self._session.execute(
            select(User).where(col(User.vk_user_id) == vk_user_id).with_for_update(),
        )
        return result.scalar_one_or_none()

    async def _get_repost_task_by_code_or_external_id(
        self,
        code: str,
        external_id: str,
    ) -> Task | None:
        result = await self._session.execute(
            select(Task)
            .where(
                col(Task.task_type) == TaskType.VK_REPOST,
                or_(
                    col(Task.code) == code,
                    col(Task.external_id) == external_id,
                ),
            )
            .with_for_update(),
        )
        return result.scalars().first()

    async def _get_completion_for_update(
        self,
        users_id: int,
        tasks_id: int,
        completion_key: str,
    ) -> TaskCompletion | None:
        result = await self._session.execute(
            select(TaskCompletion)
            .where(
                col(TaskCompletion.users_id) == users_id,
                col(TaskCompletion.tasks_id) == tasks_id,
                col(TaskCompletion.completion_key) == completion_key,
            )
            .with_for_update(),
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _to_repost_task_dto(task: Task) -> VKRepostTaskDTO:
        if task.tasks_id is None:
            raise RuntimeError("Task primary key was not generated")
        if task.external_id is None:
            raise RuntimeError("VK repost task external_id is not set")

        return VKRepostTaskDTO(
            tasks_id=task.tasks_id,
            task_name=task.task_name,
            external_id=task.external_id,
            points=task.points,
            repeat_policy=task.repeat_policy,
            week_number=task.week_number,
        )

    @staticmethod
    def _to_repost_task_creation_dto(
        status: VKRepostTaskCreationStatus,
        task: Task,
        event_id: str | None,
    ) -> VKRepostTaskCreationDTO:
        if task.tasks_id is None:
            raise RuntimeError("Task primary key was not generated")

        return VKRepostTaskCreationDTO(
            status=status,
            event_id=event_id,
            tasks_id=task.tasks_id,
            code=task.code,
            external_id=task.external_id,
            points=task.points,
            week_number=task.week_number,
        )

    @staticmethod
    def _to_completion_result(
        status: VKRepostTaskCompletionStatus,
        vk_user_id: int,
        user: User,
        completion: TaskCompletion,
        points_awarded: int,
        rejected_reason: str | None = None,
    ) -> VKRepostTaskCompletionDTO:
        if completion.task_completions_id is None:
            raise RuntimeError("TaskCompletion primary key was not generated")

        return VKRepostTaskCompletionDTO(
            status=status,
            vk_user_id=vk_user_id,
            users_id=TaskCompletionRepository._require_user_id(user=user),
            tasks_id=completion.tasks_id,
            task_completions_id=completion.task_completions_id,
            transactions_id=completion.transactions_id,
            points_awarded=points_awarded,
            balance_points=user.balance_points,
            rejected_reason=rejected_reason or completion.rejected_reason,
        )

    @staticmethod
    def _require_user_id(user: User) -> int:
        if user.users_id is None:
            raise RuntimeError("User primary key was not generated")
        return user.users_id
