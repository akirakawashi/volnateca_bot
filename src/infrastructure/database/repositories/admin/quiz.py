from datetime import UTC, datetime

from sqlalchemy import select
from sqlmodel import col

from application.admin.command.quiz import CreateQuizCommand, UpdateQuizQuestionImageCommand
from application.admin.dto.quiz import (
    CreatedQuizDTO,
    CreatedQuizOptionDTO,
    CreatedQuizQuestionDTO,
    QuizAdminDTO,
    QuizQuestionImageAdminDTO,
)
from application.admin.interface.repositories.quiz import IQuizAdminRepository
from domain.enums.task import TaskRepeatPolicy, TaskType
from infrastructure.database.models.quiz_question_options import QuizQuestionOption
from infrastructure.database.models.quiz_questions import QuizQuestion
from infrastructure.database.models.tasks import Task
from infrastructure.database.repositories.base import SQLAlchemyRepository


class QuizAdminRepository(SQLAlchemyRepository, IQuizAdminRepository):
    """Репозиторий для административных операций с квизами."""

    async def list_quizzes(self) -> tuple[QuizAdminDTO, ...]:
        now = datetime.now(tz=UTC)
        result = await self._session.execute(
            select(Task)
            .where(col(Task.task_type) == TaskType.QUIZ)
            .order_by(
                col(Task.starts_at).is_(None),
                col(Task.starts_at),
                col(Task.tasks_id),
            ),
        )
        tasks = tuple(result.scalars().all())
        if not tasks:
            return ()

        questions_by_task = await self._list_questions_by_task(
            task_ids=tuple(task.tasks_id for task in tasks if task.tasks_id is not None),
        )
        return tuple(
            self._to_quiz_admin_dto(
                task=task,
                questions=questions_by_task.get(task.tasks_id or 0, ()),
                now=now,
            )
            for task in tasks
        )

    async def create_quiz(self, command: CreateQuizCommand) -> CreatedQuizDTO:
        task = Task(
            code=command.code,
            task_name=command.task_name,
            description=command.description,
            task_type=TaskType.QUIZ,
            points=command.points,
            week_number=command.week_number,
            starts_at=command.starts_at,
            ends_at=command.ends_at,
            repeat_policy=TaskRepeatPolicy.ONCE,
            is_active=True,
        )
        self._session.add(task)
        await self._session.flush()

        created_questions: list[CreatedQuizQuestionDTO] = []
        for q_data in command.questions:
            question = QuizQuestion(
                tasks_id=task.tasks_id,
                question_text=q_data.question_text,
                image_attachment=q_data.image_attachment,
                is_active=True,
            )
            self._session.add(question)
            await self._session.flush()

            created_options: list[CreatedQuizOptionDTO] = []
            for opt_data in q_data.options:
                option = QuizQuestionOption(
                    quiz_questions_id=question.quiz_questions_id,
                    option_text=opt_data.option_text,
                    is_correct=opt_data.is_correct,
                    sort_order=opt_data.sort_order,
                )
                self._session.add(option)
                await self._session.flush()

                created_options.append(
                    CreatedQuizOptionDTO(
                        quiz_question_options_id=option.quiz_question_options_id,  # type: ignore[arg-type]
                        option_text=option.option_text,
                        is_correct=option.is_correct,
                        sort_order=option.sort_order,
                    )
                )

            created_questions.append(
                CreatedQuizQuestionDTO(
                    quiz_questions_id=question.quiz_questions_id,  # type: ignore[arg-type]
                    question_text=question.question_text,
                    image_attachment=question.image_attachment,
                    options=tuple(created_options),
                )
            )

        return CreatedQuizDTO(
            tasks_id=task.tasks_id,  # type: ignore[arg-type]
            code=task.code,
            task_name=task.task_name,
            questions=tuple(created_questions),
        )

    async def update_question_image(
        self,
        command: UpdateQuizQuestionImageCommand,
    ) -> QuizAdminDTO | None:
        result = await self._session.execute(
            select(QuizQuestion, Task)
            .join(Task, col(Task.tasks_id) == col(QuizQuestion.tasks_id))
            .where(
                col(QuizQuestion.quiz_questions_id) == command.quiz_questions_id,
                col(Task.task_type) == TaskType.QUIZ,
            )
            .with_for_update(),
        )
        row = result.one_or_none()
        if row is None:
            return None

        question, task = row
        now = datetime.now(tz=UTC)
        if not self._can_edit_quiz(task=task, now=now):
            raise ValueError("Можно редактировать изображения только у квизов с будущей датой начала")

        question.image_attachment = command.image_attachment
        await self._session.flush()

        if task.tasks_id is None:
            raise RuntimeError("Первичный ключ задания не был сгенерирован")
        questions_by_task = await self._list_questions_by_task(task_ids=(task.tasks_id,))
        return self._to_quiz_admin_dto(
            task=task,
            questions=questions_by_task.get(task.tasks_id, ()),
            now=now,
        )

    async def _list_questions_by_task(
        self,
        *,
        task_ids: tuple[int, ...],
    ) -> dict[int, tuple[QuizQuestionImageAdminDTO, ...]]:
        if not task_ids:
            return {}

        result = await self._session.execute(
            select(QuizQuestion)
            .where(col(QuizQuestion.tasks_id).in_(task_ids))
            .order_by(col(QuizQuestion.tasks_id), col(QuizQuestion.quiz_questions_id)),
        )
        grouped: dict[int, list[QuizQuestionImageAdminDTO]] = {}
        for question in result.scalars().all():
            if question.quiz_questions_id is None:
                raise RuntimeError("Первичный ключ вопроса квиза не был сгенерирован")
            grouped.setdefault(question.tasks_id, []).append(
                QuizQuestionImageAdminDTO(
                    quiz_questions_id=question.quiz_questions_id,
                    question_text=question.question_text,
                    image_attachment=question.image_attachment,
                ),
            )
        return {tasks_id: tuple(questions) for tasks_id, questions in grouped.items()}

    @classmethod
    def _to_quiz_admin_dto(
        cls,
        *,
        task: Task,
        questions: tuple[QuizQuestionImageAdminDTO, ...],
        now: datetime,
    ) -> QuizAdminDTO:
        if task.tasks_id is None:
            raise RuntimeError("Первичный ключ задания не был сгенерирован")
        return QuizAdminDTO(
            tasks_id=task.tasks_id,
            code=task.code,
            task_name=task.task_name,
            starts_at=task.starts_at,
            ends_at=task.ends_at,
            can_edit=cls._can_edit_quiz(task=task, now=now),
            questions=questions,
        )

    @staticmethod
    def _can_edit_quiz(*, task: Task, now: datetime) -> bool:
        starts_at = task.starts_at
        if starts_at is None:
            return False
        if starts_at.tzinfo is None:
            starts_at = starts_at.replace(tzinfo=UTC)
        return starts_at > now
