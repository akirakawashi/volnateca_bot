from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from application.admin.dto.quiz import QuizAdminDTO
from application.base_interactor import Interactor
from application.interface.uow import IUnitOfWork

if TYPE_CHECKING:
    from application.admin.interface.repositories.quiz import IQuizAdminRepository


@dataclass(slots=True, frozen=True, kw_only=True)
class ListQuizzesCommand:
    pass


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateQuizOptionDTO:
    option_text: str
    is_correct: bool
    sort_order: int


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateQuizQuestionDTO:
    question_text: str
    image_attachment: str | None
    options: tuple[CreateQuizOptionDTO, ...]


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateQuizCommand:
    code: str
    task_name: str
    description: str | None
    points: int
    week_number: int | None
    starts_at: datetime | None
    ends_at: datetime | None
    questions: tuple[CreateQuizQuestionDTO, ...]


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateQuizQuestionImageCommand:
    quiz_questions_id: int
    image_attachment: str | None


class ListQuizzesHandler(Interactor[ListQuizzesCommand, tuple[QuizAdminDTO, ...]]):
    def __init__(self, quiz_admin_repository: IQuizAdminRepository) -> None:
        self.quiz_admin_repository = quiz_admin_repository

    async def __call__(self, command_data: ListQuizzesCommand) -> tuple[QuizAdminDTO, ...]:
        del command_data
        return await self.quiz_admin_repository.list_quizzes()


class UpdateQuizQuestionImageHandler(
    Interactor[UpdateQuizQuestionImageCommand, QuizAdminDTO | None],
):
    def __init__(
        self,
        quiz_admin_repository: IQuizAdminRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.quiz_admin_repository = quiz_admin_repository
        self.uow = uow

    async def __call__(
        self,
        command_data: UpdateQuizQuestionImageCommand,
    ) -> QuizAdminDTO | None:
        result = await self.quiz_admin_repository.update_question_image(command_data)
        if result is None:
            return None
        await self.uow.commit()
        return result


__all__ = [
    "CreateQuizCommand",
    "CreateQuizOptionDTO",
    "CreateQuizQuestionDTO",
    "ListQuizzesCommand",
    "ListQuizzesHandler",
    "UpdateQuizQuestionImageCommand",
    "UpdateQuizQuestionImageHandler",
]
