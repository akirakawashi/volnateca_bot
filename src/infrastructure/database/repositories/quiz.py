from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlmodel import col

from application.common.dto.quiz import QuizAnswerSavedDTO, QuizQuestionDTO, QuizQuestionOptionDTO
from application.interface.repositories.quiz import IQuizRepository
from domain.enums.task import TaskCompletionStatus, TaskType
from infrastructure.database.models.quiz_answers import QuizAnswer
from infrastructure.database.models.quiz_question_options import QuizQuestionOption
from infrastructure.database.models.quiz_questions import QuizQuestion
from infrastructure.database.models.task_completions import TaskCompletion
from infrastructure.database.models.tasks import Task
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

        if await self._get_active_quiz_task_by_id(tasks_id=tasks_id) is None:
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
            select(col(QuizAnswer.quiz_questions_id)).where(
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
            image_attachment=first_unanswered.image_attachment,
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

        # Старые кнопки не должны открывать выключенную или уже недоступную викторину.
        question_result = await self._session.execute(
            select(QuizQuestion).where(
                col(QuizQuestion.quiz_questions_id) == quiz_questions_id,
                col(QuizQuestion.is_active).is_(True),
            ),
        )
        question = question_result.scalar_one_or_none()
        if question is None:
            return None

        if await self._get_active_quiz_task_by_id(tasks_id=question.tasks_id) is None:
            return QuizAnswerSavedDTO(
                is_correct=False,
                correct_option_text="",
                tasks_id=question.tasks_id,
                already_answered=False,
                quiz_unavailable=True,
            )

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

        if await self._get_active_quiz_task_by_id(tasks_id=tasks_id) is None:
            return 0

        all_ids_result = await self._session.execute(
            select(col(QuizQuestion.quiz_questions_id)).where(
                col(QuizQuestion.tasks_id) == tasks_id,
                col(QuizQuestion.is_active).is_(True),
            ),
        )
        all_ids = [row for (row,) in all_ids_result.all()]
        if not all_ids:
            return 0

        answered_result = await self._session.execute(
            select(col(QuizAnswer.quiz_questions_id)).where(
                col(QuizAnswer.users_id) == users_id,
                col(QuizAnswer.quiz_questions_id).in_(all_ids),
            ),
        )
        answered_count = len(answered_result.all())
        return max(0, len(all_ids) - answered_count)

    async def get_current_correct_quiz_streak(self, vk_user_id: int) -> int:
        users_id = await self._get_users_id_by_vk_user_id(vk_user_id=vk_user_id)
        if users_id is None:
            return 0

        completions = await self._list_completed_quiz_completions(users_id=users_id)

        streak = 0
        for completion in completions:
            if await self._is_quiz_completed_without_mistakes(
                users_id=users_id,
                tasks_id=completion.tasks_id,
            ):
                streak += 1
                continue
            break
        return streak

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

    async def _list_completed_quiz_completions(self, *, users_id: int) -> list[TaskCompletion]:
        result = await self._session.execute(
            select(TaskCompletion)
            .join(Task, col(TaskCompletion.tasks_id) == col(Task.tasks_id))
            .where(
                col(TaskCompletion.users_id) == users_id,
                col(TaskCompletion.task_completion_status) == TaskCompletionStatus.COMPLETED,
                col(Task.task_type) == TaskType.QUIZ,
            )
            .order_by(
                col(TaskCompletion.checked_at).desc(),
                col(TaskCompletion.task_completions_id).desc(),
            ),
        )
        return list(result.scalars().all())

    async def _is_quiz_completed_without_mistakes(
        self,
        *,
        users_id: int,
        tasks_id: int,
    ) -> bool:
        question_ids_result = await self._session.execute(
            select(col(QuizQuestion.quiz_questions_id)).where(
                col(QuizQuestion.tasks_id) == tasks_id,
                col(QuizQuestion.is_active).is_(True),
            ),
        )
        question_ids = [row for (row,) in question_ids_result.all()]
        if not question_ids:
            return False

        answers_result = await self._session.execute(
            select(QuizAnswer).where(
                col(QuizAnswer.users_id) == users_id,
                col(QuizAnswer.quiz_questions_id).in_(question_ids),
            ),
        )
        answers = list(answers_result.scalars().all())
        return len(answers) == len(question_ids) and all(answer.is_correct for answer in answers)

    async def _get_active_quiz_task_by_id(self, *, tasks_id: int) -> Task | None:
        now = datetime.now(tz=UTC)
        result = await self._session.execute(
            select(Task).where(
                col(Task.tasks_id) == tasks_id,
                col(Task.task_type) == TaskType.QUIZ,
                col(Task.is_active).is_(True),
                or_(col(Task.starts_at).is_(None), col(Task.starts_at) <= now),
                or_(col(Task.ends_at).is_(None), col(Task.ends_at) > now),
            ),
        )
        return result.scalar_one_or_none()
