from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlmodel import col

from application.common.dto.task import (
    QuizTaskSummary,
    TaskForAwardDTO,
    TaskSummary,
    VKLikeTaskCreationDTO,
    VKLikeTaskCreationStatus,
    VKRepostTaskCreationDTO,
    VKRepostTaskCreationStatus,
    VKUserAvailableTaskDTO,
)
from application.interface.repositories.tasks import ITaskRepository
from application.services.task_completion_key import build_task_completion_key
from domain.enums.task import TaskCompletionStatus, TaskRepeatPolicy, TaskType
from infrastructure.database.models.task_completions import TaskCompletion
from infrastructure.database.models.tasks import Task
from infrastructure.database.models.users import User
from infrastructure.database.repositories.base import SQLAlchemyRepository


class TaskRepository(SQLAlchemyRepository, ITaskRepository):
    """Репозиторий справочника заданий.

    Содержит только чтение и запись строк таблицы tasks. Никаких операций
    над балансом пользователя или фактами выполнения здесь нет.
    """

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
        existing_task = await self._get_task_by_code_or_external_id(
            code=code,
            external_id=external_id,
            task_type=TaskType.VK_REPOST,
        )
        if existing_task is not None:
            return self._to_repost_task_creation_dto(
                status=VKRepostTaskCreationStatus.ALREADY_EXISTS,
                task=existing_task,
                event_id=event_id,
            )

        try:
            async with self._session.begin_nested():
                task = self._build_task(
                    code=code,
                    task_name=task_name,
                    description=description,
                    task_type=TaskType.VK_REPOST,
                    points=points,
                    week_number=week_number,
                    external_id=external_id,
                    repeat_policy=repeat_policy,
                )
                self._session.add(task)
                await self._session.flush()
        except IntegrityError:
            existing_task = await self._get_task_by_code_or_external_id(
                code=code,
                external_id=external_id,
                task_type=TaskType.VK_REPOST,
            )
            if existing_task is None:
                raise
            return self._to_repost_task_creation_dto(
                status=VKRepostTaskCreationStatus.ALREADY_EXISTS,
                task=existing_task,
                event_id=event_id,
            )
        return self._to_repost_task_creation_dto(
            status=VKRepostTaskCreationStatus.CREATED,
            task=task,
            event_id=event_id,
        )

    async def get_active_repost_task_by_external_ids(
        self,
        external_ids: tuple[str, ...],
    ) -> TaskSummary | None:
        task = await self._get_active_task_by_external_ids(
            external_ids=external_ids,
            task_type=TaskType.VK_REPOST,
        )
        if task is None:
            return None
        return self._to_task_summary(task=task)

    async def get_or_create_subscription_task(
        self,
        code: str,
        task_name: str,
        description: str,
        external_id: str,
        points: int,
        week_number: int | None,
        repeat_policy: TaskRepeatPolicy,
    ) -> TaskSummary:
        existing_task = await self._get_task_by_code_or_external_id(
            code=code,
            external_id=external_id,
            task_type=TaskType.VK_SUBSCRIBE,
        )
        if existing_task is not None:
            return self._to_task_summary(task=existing_task)

        try:
            async with self._session.begin_nested():
                task = self._build_task(
                    code=code,
                    task_name=task_name,
                    description=description,
                    task_type=TaskType.VK_SUBSCRIBE,
                    points=points,
                    week_number=week_number,
                    external_id=external_id,
                    repeat_policy=repeat_policy,
                )
                self._session.add(task)
                await self._session.flush()
        except IntegrityError:
            existing_task = await self._get_task_by_code_or_external_id(
                code=code,
                external_id=external_id,
                task_type=TaskType.VK_SUBSCRIBE,
            )
            if existing_task is None:
                raise
            return self._to_task_summary(task=existing_task)
        return self._to_task_summary(task=task)

    async def create_like_task_if_not_exists(
        self,
        code: str,
        task_name: str,
        description: str,
        external_id: str,
        points: int,
        week_number: int | None,
        repeat_policy: TaskRepeatPolicy,
        event_id: str | None,
    ) -> VKLikeTaskCreationDTO:
        existing_task = await self._get_task_by_code_or_external_id(
            code=code,
            external_id=external_id,
            task_type=TaskType.VK_LIKE,
        )
        if existing_task is not None:
            return self._to_like_task_creation_dto(
                status=VKLikeTaskCreationStatus.ALREADY_EXISTS,
                task=existing_task,
                event_id=event_id,
            )

        try:
            async with self._session.begin_nested():
                task = self._build_task(
                    code=code,
                    task_name=task_name,
                    description=description,
                    task_type=TaskType.VK_LIKE,
                    points=points,
                    week_number=week_number,
                    external_id=external_id,
                    repeat_policy=repeat_policy,
                )
                self._session.add(task)
                await self._session.flush()
        except IntegrityError:
            existing_task = await self._get_task_by_code_or_external_id(
                code=code,
                external_id=external_id,
                task_type=TaskType.VK_LIKE,
            )
            if existing_task is None:
                raise
            return self._to_like_task_creation_dto(
                status=VKLikeTaskCreationStatus.ALREADY_EXISTS,
                task=existing_task,
                event_id=event_id,
            )
        return self._to_like_task_creation_dto(
            status=VKLikeTaskCreationStatus.CREATED,
            task=task,
            event_id=event_id,
        )

    async def get_active_like_task_by_external_ids(
        self,
        external_ids: tuple[str, ...],
    ) -> TaskSummary | None:
        task = await self._get_active_task_by_external_ids(
            external_ids=external_ids,
            task_type=TaskType.VK_LIKE,
        )
        if task is None:
            return None
        return self._to_task_summary(task=task)

    async def list_available_tasks_for_vk_user(
        self,
        vk_user_id: int,
    ) -> list[VKUserAvailableTaskDTO]:
        users_id = await self._get_users_id_by_vk_user_id(vk_user_id=vk_user_id)
        if users_id is None:
            return []

        now = datetime.now(tz=UTC)
        tasks = await self._list_active_tasks(now=now)
        completed_keys = await self._list_completed_task_keys(users_id=users_id)

        return [
            self._to_user_available_task_dto(task=task)
            for task in tasks
            if not self._is_task_completed_for_current_period(
                task=task,
                checked_at=now,
                completed_keys=completed_keys,
            )
        ]

    async def get_active_quiz_task_for_vk_user(
        self,
        vk_user_id: int,
    ) -> QuizTaskSummary | None:
        """Возвращает первое активное задание типа QUIZ, которое пользователь ещё не выполнил.

        Возвращает None если:
        - пользователь не зарегистрирован,
        - нет активных квиз-заданий,
        - все квиз-задания уже выполнены.
        """
        users_id = await self._get_users_id_by_vk_user_id(vk_user_id=vk_user_id)
        if users_id is None:
            return None

        now = datetime.now(tz=UTC)
        result = await self._session.execute(
            select(Task)
            .where(
                col(Task.task_type) == TaskType.QUIZ,
                col(Task.is_active).is_(True),
                or_(col(Task.starts_at).is_(None), col(Task.starts_at) <= now),
                or_(col(Task.ends_at).is_(None), col(Task.ends_at) > now),
            )
            .order_by(col(Task.starts_at), col(Task.tasks_id)),
        )
        quiz_tasks = list(result.scalars().all())
        if not quiz_tasks:
            return None

        completed_keys = await self._list_completed_task_keys(users_id=users_id)

        for task in quiz_tasks:
            if not self._is_task_completed_for_current_period(
                task=task,
                checked_at=now,
                completed_keys=completed_keys,
            ):
                return self._to_quiz_task_summary(task=task, checked_at=now)

        return None

    async def is_week_completed_by_vk_user(
        self,
        *,
        vk_user_id: int,
        week_number: int,
    ) -> bool:
        users_id = await self._get_users_id_by_vk_user_id(vk_user_id=vk_user_id)
        if users_id is None:
            return False

        now = datetime.now(tz=UTC)
        weekly_tasks = await self._list_active_tasks_by_week(week_number=week_number)
        if not weekly_tasks:
            return False

        completed_keys = await self._list_completed_task_keys(users_id=users_id)
        return all(
            self._is_task_completed_for_current_period(
                task=task,
                checked_at=now,
                completed_keys=completed_keys,
            )
            for task in weekly_tasks
        )

    async def _get_users_id_by_vk_user_id(self, vk_user_id: int) -> int | None:
        result = await self._session.execute(
            select(User).where(col(User.vk_user_id) == vk_user_id),
        )
        user = result.scalar_one_or_none()
        return user.users_id if user is not None else None

    async def _list_active_tasks(self, now: datetime) -> list[Task]:
        result = await self._session.execute(
            select(Task)
            .where(
                col(Task.is_active).is_(True),
                col(Task.task_type) != TaskType.QUIZ,
                or_(col(Task.starts_at).is_(None), col(Task.starts_at) <= now),
                or_(col(Task.ends_at).is_(None), col(Task.ends_at) > now),
            )
            .order_by(col(Task.week_number), col(Task.tasks_id)),
        )
        return list(result.scalars().all())

    async def _list_active_tasks_by_week(
        self,
        *,
        week_number: int,
    ) -> list[Task]:
        result = await self._session.execute(
            select(Task)
            .where(
                col(Task.is_active).is_(True),
                col(Task.week_number) == week_number,
            )
            .order_by(col(Task.tasks_id)),
        )
        return list(result.scalars().all())

    async def _list_completed_task_keys(self, users_id: int) -> set[tuple[int, str]]:
        result = await self._session.execute(
            select(TaskCompletion).where(
                col(TaskCompletion.users_id) == users_id,
                col(TaskCompletion.task_completion_status) == TaskCompletionStatus.COMPLETED,
            ),
        )
        return {(completion.tasks_id, completion.completion_key) for completion in result.scalars().all()}

    async def _get_task_by_code_or_external_id(
        self,
        code: str,
        external_id: str,
        task_type: TaskType,
    ) -> Task | None:
        result = await self._session.execute(
            select(Task)
            .where(
                col(Task.task_type) == task_type,
                or_(
                    col(Task.code) == code,
                    col(Task.external_id) == external_id,
                ),
            )
            .with_for_update(),
        )
        return result.scalars().first()

    async def _get_active_task_by_external_ids(
        self,
        external_ids: tuple[str, ...],
        task_type: TaskType,
    ) -> Task | None:
        if not external_ids:
            return None

        now = datetime.now(tz=UTC)
        result = await self._session.execute(
            select(Task)
            .where(
                col(Task.task_type) == task_type,
                col(Task.external_id).in_(external_ids),
                col(Task.is_active).is_(True),
                or_(col(Task.starts_at).is_(None), col(Task.starts_at) <= now),
                or_(col(Task.ends_at).is_(None), col(Task.ends_at) > now),
            )
            .order_by(col(Task.tasks_id)),
        )
        return result.scalars().first()

    @staticmethod
    def _build_task(
        *,
        code: str,
        task_name: str,
        description: str,
        task_type: TaskType,
        points: int,
        week_number: int | None,
        external_id: str,
        repeat_policy: TaskRepeatPolicy,
    ) -> Task:
        return Task(
            code=code,
            task_name=task_name,
            description=description,
            task_type=task_type,
            points=points,
            week_number=week_number,
            external_id=external_id,
            repeat_policy=repeat_policy,
            is_active=True,
        )

    @staticmethod
    def _is_task_completed_for_current_period(
        *,
        task: Task,
        checked_at: datetime,
        completed_keys: set[tuple[int, str]],
    ) -> bool:
        if task.tasks_id is None:
            raise RuntimeError("Первичный ключ задания не был сгенерирован")
        completion_key = build_task_completion_key(
            repeat_policy=task.repeat_policy,
            week_number=task.week_number,
            checked_at=checked_at,
        )
        return (task.tasks_id, completion_key) in completed_keys

    @staticmethod
    def _to_user_available_task_dto(task: Task) -> VKUserAvailableTaskDTO:
        if task.tasks_id is None:
            raise RuntimeError("Первичный ключ задания не был сгенерирован")

        return VKUserAvailableTaskDTO(
            tasks_id=task.tasks_id,
            task_name=task.task_name,
            task_type=task.task_type,
            external_id=task.external_id,
            points=task.points,
            repeat_policy=task.repeat_policy,
            week_number=task.week_number,
        )

    @staticmethod
    def _to_task_summary(task: Task) -> TaskSummary:
        if task.tasks_id is None:
            raise RuntimeError("Первичный ключ задания не был сгенерирован")

        return TaskSummary(
            tasks_id=task.tasks_id,
            task_name=task.task_name,
            external_id=task.external_id,
            points=task.points,
            repeat_policy=task.repeat_policy,
            week_number=task.week_number,
        )

    @staticmethod
    def _to_quiz_task_summary(task: Task, checked_at: datetime) -> QuizTaskSummary:
        if task.tasks_id is None:
            raise RuntimeError("Первичный ключ задания не был сгенерирован")

        completion_key = build_task_completion_key(
            repeat_policy=task.repeat_policy,
            week_number=task.week_number,
            checked_at=checked_at,
        )
        return QuizTaskSummary(
            tasks_id=task.tasks_id,
            task_name=task.task_name,
            points=task.points,
            repeat_policy=task.repeat_policy,
            week_number=task.week_number,
            completion_key=completion_key,
        )

    @staticmethod
    def _to_repost_task_creation_dto(
        status: VKRepostTaskCreationStatus,
        task: Task,
        event_id: str | None,
    ) -> VKRepostTaskCreationDTO:
        if task.tasks_id is None:
            raise RuntimeError("Первичный ключ задания не был сгенерирован")

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
    def _to_like_task_creation_dto(
        status: VKLikeTaskCreationStatus,
        task: Task,
        event_id: str | None,
    ) -> VKLikeTaskCreationDTO:
        if task.tasks_id is None:
            raise RuntimeError("Первичный ключ задания не был сгенерирован")

        return VKLikeTaskCreationDTO(
            status=status,
            event_id=event_id,
            tasks_id=task.tasks_id,
            code=task.code,
            external_id=task.external_id,
            points=task.points,
            week_number=task.week_number,
        )

    async def get_task_for_award(self, tasks_id: int) -> TaskForAwardDTO | None:
        result = await self._session.execute(
            select(Task).where(col(Task.tasks_id) == tasks_id),
        )
        task = result.scalar_one_or_none()
        if task is None or task.tasks_id is None:
            return None
        return TaskForAwardDTO(
            tasks_id=task.tasks_id,
            task_name=task.task_name,
            points=task.points,
            repeat_policy=task.repeat_policy,
            week_number=task.week_number,
        )
