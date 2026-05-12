from abc import ABC, abstractmethod

from application.admin.dto.quiz import CreateQuizCommand, CreatedQuizDTO


class IQuizAdminRepository(ABC):
    @abstractmethod
    async def create_quiz(self, command: CreateQuizCommand) -> CreatedQuizDTO:
        """Создаёт задание типа QUIZ вместе с вопросами и вариантами ответов."""
        raise NotImplementedError
