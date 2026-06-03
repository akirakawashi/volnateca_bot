from dataclasses import dataclass

from application.base_interactor import Interactor
from application.common.dto.task import (
    QuizTaskSummary,
    TaskPaginationDTO,
    VKUserAvailableTaskDTO,
)
from application.common.helpers import normalize_page
from application.interface.repositories.tasks import ITaskRepository
from domain.project_rules import TASKS_PAGE_SIZE


@dataclass(slots=True, frozen=True, kw_only=True)
class GetVKUserTasksCommand:
    vk_user_id: int
    page: int = 1


@dataclass(slots=True, frozen=True, kw_only=True)
class GetVKUserTasksDTO:
    vk_user_id: int
    tasks: tuple[VKUserAvailableTaskDTO, ...]
    active_quiz: QuizTaskSummary | None
    page_tasks: tuple[VKUserAvailableTaskDTO, ...] = ()
    pagination: TaskPaginationDTO | None = None


class GetVKUserTasksHandler(Interactor[GetVKUserTasksCommand, GetVKUserTasksDTO]):
    """Возвращает активные задания, которые пользователь ещё может выполнить."""

    def __init__(self, task_repository: ITaskRepository) -> None:
        self.task_repository = task_repository

    async def __call__(self, command_data: GetVKUserTasksCommand) -> GetVKUserTasksDTO:
        tasks = await self.task_repository.list_available_tasks_for_vk_user(
            vk_user_id=command_data.vk_user_id,
        )
        total_items = len(tasks)
        total_pages = max(1, (total_items + TASKS_PAGE_SIZE - 1) // TASKS_PAGE_SIZE)
        page = normalize_page(page=command_data.page, total_pages=total_pages)
        start = (page - 1) * TASKS_PAGE_SIZE
        page_tasks = tuple(tasks[start : start + TASKS_PAGE_SIZE])
        active_quiz = await self.task_repository.get_active_quiz_task_for_vk_user(
            vk_user_id=command_data.vk_user_id,
        )
        return GetVKUserTasksDTO(
            vk_user_id=command_data.vk_user_id,
            tasks=tuple(tasks),
            active_quiz=active_quiz,
            page_tasks=page_tasks,
            pagination=TaskPaginationDTO(
                page=page,
                page_size=TASKS_PAGE_SIZE,
                total_items=total_items,
                total_pages=total_pages,
                has_previous=page > 1,
                has_next=page < total_pages,
            ),
        )
