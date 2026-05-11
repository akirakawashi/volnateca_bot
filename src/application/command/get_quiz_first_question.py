from dataclasses import dataclass

from application.base_interactor import Interactor
from application.common.dto.quiz import QuizQuestionDTO
from application.interface.repositories.quiz import IQuizRepository


@dataclass(slots=True, frozen=True, kw_only=True)
class GetQuizFirstQuestionCommand:
    tasks_id: int
    vk_user_id: int


class GetQuizFirstQuestionHandler(
    Interactor[GetQuizFirstQuestionCommand, QuizQuestionDTO | None],
):
    """Возвращает первый неотвеченный вопрос квиза для пользователя."""

    def __init__(self, quiz_repository: IQuizRepository) -> None:
        self.quiz_repository = quiz_repository

    async def __call__(
        self,
        command_data: GetQuizFirstQuestionCommand,
    ) -> QuizQuestionDTO | None:
        return await self.quiz_repository.get_first_unanswered_question(
            tasks_id=command_data.tasks_id,
            vk_user_id=command_data.vk_user_id,
        )
