from datetime import datetime

from sqlalchemy import select
from sqlmodel import col

from application.common.dto.task_completion import TaskCompletionRecord
from application.interface.repositories.task_completions import ITaskCompletionRepository
from domain.enums.task import TaskCompletionStatus
from infrastructure.database.models.task_completions import TaskCompletion
from infrastructure.database.models.users import User
from infrastructure.database.repositories.base import SQLAlchemyRepository


class TaskCompletionRepository(SQLAlchemyRepository, ITaskCompletionRepository):
    async def get_for_update(
        self,
        *,
        users_id: int,
        tasks_id: int,
        completion_key: str,
    ) -> TaskCompletionRecord | None:
        result = await self._session.execute(
            select(TaskCompletion)
            .where(
                col(TaskCompletion.users_id) == users_id,
                col(TaskCompletion.tasks_id) == tasks_id,
                col(TaskCompletion.completion_key) == completion_key,
            )
            .with_for_update(),
        )
        completion = result.scalar_one_or_none()
        if completion is None:
            return None
        return self._to_record(completion=completion)

    async def create(
        self,
        *,
        users_id: int,
        tasks_id: int,
        completion_key: str,
        task_completion_status: TaskCompletionStatus,
        points_awarded: int,
        transactions_id: int | None,
        external_event_id: str | None,
        evidence_external_id: str | None,
        rejected_reason: str | None,
        checked_at: datetime,
    ) -> TaskCompletionRecord:
        completion = TaskCompletion(
            users_id=users_id,
            tasks_id=tasks_id,
            completion_key=completion_key,
            transactions_id=transactions_id,
            task_completion_status=task_completion_status,
            points_awarded=points_awarded,
            external_event_id=external_event_id,
            evidence_external_id=evidence_external_id,
            rejected_reason=rejected_reason,
            checked_at=checked_at,
        )
        self._session.add(completion)
        await self._session.flush()
        return self._to_record(completion=completion)

    async def update_status(
        self,
        *,
        task_completions_id: int,
        task_completion_status: TaskCompletionStatus,
        points_awarded: int,
        transactions_id: int | None,
        external_event_id: str | None,
        evidence_external_id: str | None,
        rejected_reason: str | None,
        checked_at: datetime,
    ) -> TaskCompletionRecord:
        completion = await self._session.get(TaskCompletion, task_completions_id)
        if completion is None:
            raise RuntimeError(
                f"TaskCompletion with task_completions_id={task_completions_id} was not found",
            )

        completion.task_completion_status = task_completion_status
        completion.points_awarded = points_awarded
        completion.transactions_id = transactions_id
        completion.external_event_id = external_event_id
        completion.evidence_external_id = evidence_external_id
        completion.rejected_reason = rejected_reason
        completion.checked_at = checked_at

        await self._session.flush()
        return self._to_record(completion=completion)

    async def is_completed_by_vk_user(
        self,
        *,
        vk_user_id: int,
        tasks_id: int,
        completion_key: str,
    ) -> bool:
        result = await self._session.execute(
            select(TaskCompletion)
            .join(User, col(TaskCompletion.users_id) == col(User.users_id))
            .where(
                col(User.vk_user_id) == vk_user_id,
                col(TaskCompletion.tasks_id) == tasks_id,
                col(TaskCompletion.completion_key) == completion_key,
                col(TaskCompletion.task_completion_status) == TaskCompletionStatus.COMPLETED,
            ),
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _to_record(completion: TaskCompletion) -> TaskCompletionRecord:
        if completion.task_completions_id is None:
            raise RuntimeError("TaskCompletion primary key was not generated")

        return TaskCompletionRecord(
            task_completions_id=completion.task_completions_id,
            users_id=completion.users_id,
            tasks_id=completion.tasks_id,
            completion_key=completion.completion_key,
            transactions_id=completion.transactions_id,
            task_completion_status=completion.task_completion_status,
            points_awarded=completion.points_awarded,
            external_event_id=completion.external_event_id,
            evidence_external_id=completion.evidence_external_id,
            rejected_reason=completion.rejected_reason,
            checked_at=completion.checked_at,
        )
