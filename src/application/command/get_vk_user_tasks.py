from dataclasses import dataclass

from application.base_interactor import Interactor
from application.common.dto.task import VKUserAvailableTaskDTO
from application.interface.repositories.tasks import ITaskRepository


@dataclass(slots=True, frozen=True, kw_only=True)
class GetVKUserTasksCommand:
    vk_user_id: int


@dataclass(slots=True, frozen=True, kw_only=True)
class GetVKUserTasksDTO:
    vk_user_id: int
    tasks: tuple[VKUserAvailableTaskDTO, ...]


class GetVKUserTasksHandler(Interactor[GetVKUserTasksCommand, GetVKUserTasksDTO]):
    """Возвращает активные задания, которые пользователь ещё может выполнить."""

    def __init__(self, task_repository: ITaskRepository) -> None:
        self.task_repository = task_repository

    async def __call__(self, command_data: GetVKUserTasksCommand) -> GetVKUserTasksDTO:
        tasks = await self.task_repository.list_available_tasks_for_vk_user(
            vk_user_id=command_data.vk_user_id,
        )
        return GetVKUserTasksDTO(
            vk_user_id=command_data.vk_user_id,
            tasks=tuple(tasks),
        )
