from abc import ABC, abstractmethod

from application.common.dto.quiz import QuizAnswerSavedDTO, QuizQuestionDTO


class IQuizRepository(ABC):
    @abstractmethod
    async def get_first_unanswered_question(
        self,
        tasks_id: int,
        vk_user_id: int,
    ) -> QuizQuestionDTO | None:
        """Возвращает первый неотвеченный вопрос квиза для пользователя.

        Возвращает None, если все вопросы уже отвечены или задание не найдено.
        """
        raise NotImplementedError

    @abstractmethod
    async def save_answer(
        self,
        vk_user_id: int,
        quiz_questions_id: int,
        quiz_question_options_id: int,
    ) -> QuizAnswerSavedDTO | None:
        """Сохраняет ответ пользователя на вопрос.

        Возвращает None если вариант ответа не принадлежит вопросу.
        `already_answered=True` если пользователь уже отвечал на этот вопрос.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_remaining_questions_count(
        self,
        tasks_id: int,
        vk_user_id: int,
    ) -> int:
        """Возвращает количество активных неотвеченных вопросов в задании."""
        raise NotImplementedError


__all__ = ["IQuizRepository"]
