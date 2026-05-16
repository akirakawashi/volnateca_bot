from application.admin.dto.quiz import (
    CreateQuizCommand,
    CreatedQuizDTO,
    CreatedQuizOptionDTO,
    CreatedQuizQuestionDTO,
)
from application.admin.interface.repositories.quiz import IQuizAdminRepository
from domain.enums.task import TaskRepeatPolicy, TaskType
from infrastructure.database.models.quiz_question_options import QuizQuestionOption
from infrastructure.database.models.quiz_questions import QuizQuestion
from infrastructure.database.models.tasks import Task
from infrastructure.database.repositories.base import SQLAlchemyRepository


class QuizAdminRepository(SQLAlchemyRepository, IQuizAdminRepository):
    """Репозиторий для административных операций с квизами."""

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
