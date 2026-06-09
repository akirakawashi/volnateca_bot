from abc import ABC, abstractmethod

from application.admin.command.quiz import CreateQuizCommand, UpdateQuizQuestionImageCommand
from application.admin.dto.quiz import CreatedQuizDTO, QuizAdminDTO


class IQuizAdminRepository(ABC):
    @abstractmethod
    async def list_quizzes(self) -> tuple[QuizAdminDTO, ...]:
        raise NotImplementedError

    @abstractmethod
    async def create_quiz(self, command: CreateQuizCommand) -> CreatedQuizDTO:
        """Создаёт задание типа QUIZ вместе с вопросами и вариантами ответов."""
        raise NotImplementedError

    @abstractmethod
    async def update_question_image(
        self,
        command: UpdateQuizQuestionImageCommand,
    ) -> QuizAdminDTO | None:
        raise NotImplementedError
