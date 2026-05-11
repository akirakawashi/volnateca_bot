from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlmodel import col

from application.common.dto.quiz import QuizAnswerSavedDTO, QuizQuestionDTO, QuizQuestionOptionDTO
from application.interface.repositories.quiz import IQuizRepository
from infrastructure.database.models.quiz_answers import QuizAnswer
from infrastructure.database.models.quiz_question_options import QuizQuestionOption
from infrastructure.database.models.quiz_questions import QuizQuestion
from infrastructure.database.models.users import User
from infrastructure.database.repositories.base import SQLAlchemyRepository


class QuizRepository(SQLAlchemyRepository, IQuizRepository):
    """Репозиторий для работы с вопросами и ответами квиза."""

    async def get_first_unanswered_question(
        self,
        tasks_id: int,
        vk_user_id: int,
    ) -> QuizQuestionDTO | None:
        """Возвращает первый активный вопрос задания, на который пользователь ещё не отвечал."""

        users_id = await self._get_users_id_by_vk_user_id(vk_user_id=vk_user_id)
        if users_id is None:
            return None

        # Все активные вопросы задания (упорядоченные)
        result = await self._session.execute(
            select(QuizQuestion)
            .where(
                col(QuizQuestion.tasks_id) == tasks_id,
                col(QuizQuestion.is_active).is_(True),
            )
            .order_by(col(QuizQuestion.quiz_questions_id)),
        )
        all_questions = list(result.scalars().all())
        if not all_questions:
            return None

        total_questions = len(all_questions)

        # ID уже отвеченных вопросов для этого пользователя в этом задании
        question_ids = [q.quiz_questions_id for q in all_questions]
        answered_result = await self._session.execute(
            select(QuizAnswer.quiz_questions_id).where(
                col(QuizAnswer.users_id) == users_id,
                col(QuizAnswer.quiz_questions_id).in_(question_ids),
            ),
        )
        answered_ids = {row for (row,) in answered_result.all()}

        first_unanswered: QuizQuestion | None = None
        question_number = 0
        for idx, question in enumerate(all_questions, start=1):
            if question.quiz_questions_id not in answered_ids:
                first_unanswered = question
                question_number = idx
                break

        if first_unanswered is None or first_unanswered.quiz_questions_id is None:
            return None

        # Варианты ответов для найденного вопроса
        options_result = await self._session.execute(
            select(QuizQuestionOption)
            .where(
                col(QuizQuestionOption.quiz_questions_id) == first_unanswered.quiz_questions_id,
            )
            .order_by(col(QuizQuestionOption.sort_order), col(QuizQuestionOption.quiz_question_options_id)),
        )
        options = list(options_result.scalars().all())

        return QuizQuestionDTO(
            quiz_questions_id=first_unanswered.quiz_questions_id,
            question_text=first_unanswered.question_text,
            image_url=first_unanswered.image_url,
            question_number=question_number,
            total_questions=total_questions,
            options=tuple(
                QuizQuestionOptionDTO(
                    quiz_question_options_id=opt.quiz_question_options_id,  # type: ignore[arg-type]
                    option_text=opt.option_text,
                )
                for opt in options
            ),
        )

    async def save_answer(
        self,
        vk_user_id: int,
        quiz_questions_id: int,
        quiz_question_options_id: int,
    ) -> QuizAnswerSavedDTO | None:
        """Сохраняет ответ пользователя. None если option не принадлежит question."""
        users_id = await self._get_users_id_by_vk_user_id(vk_user_id=vk_user_id)
        if users_id is None:
            return None

        # Проверяем принадлежность варианта ответа вопросу
        option_result = await self._session.execute(
            select(QuizQuestionOption).where(
                col(QuizQuestionOption.quiz_question_options_id) == quiz_question_options_id,
                col(QuizQuestionOption.quiz_questions_id) == quiz_questions_id,
            ),
        )
        option = option_result.scalar_one_or_none()
        if option is None:
            return None

        # Правильный вариант ответа для обратной связи
        correct_result = await self._session.execute(
            select(QuizQuestionOption).where(
                col(QuizQuestionOption.quiz_questions_id) == quiz_questions_id,
                col(QuizQuestionOption.is_correct).is_(True),
            ),
        )
        correct_option = correct_result.scalar_one_or_none()

        # tasks_id из вопроса
        question_result = await self._session.execute(
            select(QuizQuestion).where(
                col(QuizQuestion.quiz_questions_id) == quiz_questions_id,
            ),
        )
        question = question_result.scalar_one_or_none()
        if question is None:
            return None

        correct_text = correct_option.option_text if correct_option is not None else ""

        # Сохраняем ответ с защитой от дублирования
        try:
            async with self._session.begin_nested():
                answer = QuizAnswer(
                    users_id=users_id,
                    quiz_questions_id=quiz_questions_id,
                    quiz_question_options_id=quiz_question_options_id,
                    is_correct=option.is_correct,
                )
                self._session.add(answer)
                await self._session.flush()
        except IntegrityError:
            return QuizAnswerSavedDTO(
                is_correct=option.is_correct,
                correct_option_text=correct_text,
                tasks_id=question.tasks_id,
                already_answered=True,
            )

        return QuizAnswerSavedDTO(
            is_correct=option.is_correct,
            correct_option_text=correct_text,
            tasks_id=question.tasks_id,
            already_answered=False,
            quiz_answers_id=answer.quiz_answers_id,
        )

    async def get_remaining_questions_count(
        self,
        tasks_id: int,
        vk_user_id: int,
    ) -> int:
        """Возвращает количество активных неотвеченных вопросов в задании."""
        users_id = await self._get_users_id_by_vk_user_id(vk_user_id=vk_user_id)
        if users_id is None:
            return 0

        all_ids_result = await self._session.execute(
            select(QuizQuestion.quiz_questions_id).where(
                col(QuizQuestion.tasks_id) == tasks_id,
                col(QuizQuestion.is_active).is_(True),
            ),
        )
        all_ids = [row for (row,) in all_ids_result.all()]
        if not all_ids:
            return 0

        answered_result = await self._session.execute(
            select(QuizAnswer.quiz_questions_id).where(
                col(QuizAnswer.users_id) == users_id,
                col(QuizAnswer.quiz_questions_id).in_(all_ids),
            ),
        )
        answered_count = len(answered_result.all())
        return max(0, len(all_ids) - answered_count)

    async def link_answer_to_task_completion(
        self,
        quiz_answers_id: int,
        task_completions_id: int,
    ) -> None:
        """Проставляет task_completions_id на запись ответа, завершившего квиз."""
        result = await self._session.execute(
            select(QuizAnswer).where(col(QuizAnswer.quiz_answers_id) == quiz_answers_id),
        )
        answer = result.scalar_one_or_none()
        if answer is not None:
            answer.task_completions_id = task_completions_id
            self._session.add(answer)

    async def _get_users_id_by_vk_user_id(self, vk_user_id: int) -> int | None:
        result = await self._session.execute(
            select(User).where(col(User.vk_user_id) == vk_user_id),
        )
        user = result.scalar_one_or_none()
        return user.users_id if user is not None else None
