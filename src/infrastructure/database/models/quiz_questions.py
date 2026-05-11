from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Text, func
from sqlmodel import Column, Field, Relationship

from infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from infrastructure.database.models.quiz_answers import QuizAnswer
    from infrastructure.database.models.quiz_question_options import QuizQuestionOption
    from infrastructure.database.models.tasks import Task


class QuizQuestion(BaseModel, table=True):
    """
    Вопрос викторины, привязанный к заданию типа QUIZ.

    Одно задание может содержать один или несколько вопросов.
    Варианты ответов хранятся в quiz_question_options.
    """

    __tablename__ = "quiz_questions"

    quiz_questions_id: int | None = Field(default=None, primary_key=True)
    tasks_id: int = Field(
        foreign_key="tasks.tasks_id",
        nullable=False,
        index=True,
        description="ID задания типа QUIZ, к которому относится вопрос",
    )
    question_text: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Текст вопроса, отображаемый пользователю",
    )
    image_url: str | None = Field(
        default=None,
        description="URL изображения к вопросу; NULL если картинки нет",
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
        index=True,
        description="Участвует ли вопрос в выдаче пользователям",
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )

    task: "Task" = Relationship(back_populates="quiz_questions")
    options: list["QuizQuestionOption"] = Relationship(back_populates="quiz_question")
    answers: list["QuizAnswer"] = Relationship(back_populates="quiz_question")
