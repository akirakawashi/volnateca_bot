from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, UniqueConstraint, func
from sqlmodel import Column, Field, Relationship

from infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from infrastructure.database.models.quiz_question_options import QuizQuestionOption
    from infrastructure.database.models.quiz_questions import QuizQuestion
    from infrastructure.database.models.task_completions import TaskCompletion
    from infrastructure.database.models.users import User


class QuizAnswer(BaseModel, table=True):
    """
    Ответ пользователя на вопрос викторины.

    Один пользователь может ответить на один вопрос ровно один раз
    (UniqueConstraint на users_id + quiz_questions_id).
    Поле is_correct денормализовано для быстрого подсчёта серий правильных ответов.
    """

    __tablename__ = "quiz_answers"
    __table_args__ = (
        UniqueConstraint(
            "users_id",
            "quiz_questions_id",
            name="uq_quiz_answers_users_question",
        ),
    )

    quiz_answers_id: int | None = Field(default=None, primary_key=True)
    users_id: int = Field(
        foreign_key="users.users_id",
        nullable=False,
        index=True,
        description="ID пользователя, который ответил на вопрос",
    )
    quiz_questions_id: int = Field(
        foreign_key="quiz_questions.quiz_questions_id",
        nullable=False,
        index=True,
        description="ID вопроса, на который дан ответ",
    )
    quiz_question_options_id: int = Field(
        foreign_key="quiz_question_options.quiz_question_options_id",
        nullable=False,
        index=True,
        description="ID выбранного пользователем варианта ответа",
    )
    is_correct: bool = Field(
        nullable=False,
        description="Правильный ли ответ выбрал пользователь; денормализовано для удобства подсчёта стриков",
    )
    task_completions_id: int | None = Field(
        default=None,
        foreign_key="task_completions.task_completions_id",
        unique=True,
        description="ID записи выполнения задания, связанной с этим ответом; NULL если задание не было начислено",
    )
    answered_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
        description="Дата и время, когда пользователь дал ответ",
    )

    user: "User" = Relationship(back_populates="quiz_answers")
    quiz_question: "QuizQuestion" = Relationship(back_populates="answers")
    selected_option: "QuizQuestionOption" = Relationship(back_populates="answers")
    task_completion: Optional["TaskCompletion"] = Relationship(back_populates="quiz_answer")
