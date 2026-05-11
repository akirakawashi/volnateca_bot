from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, func
from sqlmodel import Column, Field, Relationship

from infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from infrastructure.database.models.quiz_answers import QuizAnswer
    from infrastructure.database.models.quiz_questions import QuizQuestion


class QuizQuestionOption(BaseModel, table=True):
    """
    Вариант ответа на вопрос викторины.

    Каждый вопрос имеет несколько вариантов, ровно один из которых
    является правильным (is_correct=True).
    """

    __tablename__ = "quiz_question_options"

    quiz_question_options_id: int | None = Field(default=None, primary_key=True)
    quiz_questions_id: int = Field(
        foreign_key="quiz_questions.quiz_questions_id",
        nullable=False,
        index=True,
        description="ID вопроса, к которому относится вариант ответа",
    )
    option_text: str = Field(
        nullable=False,
        description="Текст варианта ответа",
    )
    is_correct: bool = Field(
        default=False,
        nullable=False,
        description="Является ли этот вариант правильным ответом",
    )
    sort_order: int = Field(
        default=0,
        nullable=False,
        description="Порядок отображения варианта ответа пользователю",
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )

    quiz_question: "QuizQuestion" = Relationship(back_populates="options")
    answers: list["QuizAnswer"] = Relationship(back_populates="selected_option")
