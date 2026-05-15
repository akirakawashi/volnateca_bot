import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from application.admin.dto.quiz import (
    CreateQuizCommand,
    CreateQuizOptionDTO,
    CreateQuizQuestionDTO,
    CreatedQuizDTO,
)


# ── Request ───────────────────────────────────────────────────────────────────

class CreateQuizOptionSchema(BaseModel):
    option_text: str = Field(min_length=1, max_length=500)
    is_correct: bool
    sort_order: int = Field(ge=0)


class CreateQuizQuestionSchema(BaseModel):
    question_text: str = Field(min_length=1, max_length=2000)
    image_url: str | None = None
    options: list[CreateQuizOptionSchema] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_exactly_one_correct(self) -> "CreateQuizQuestionSchema":
        correct_count = sum(1 for o in self.options if o.is_correct)
        if correct_count != 1:
            raise ValueError("Каждый вопрос должен содержать ровно один правильный вариант ответа")
        return self


class CreateQuizRequestSchema(BaseModel):
    task_name: str = Field(min_length=1, max_length=500)
    description: str | None = None
    points: int = Field(gt=0)
    week_number: int | None = Field(default=None, ge=1, le=12)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    questions: list[CreateQuizQuestionSchema] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_dates(self) -> "CreateQuizRequestSchema":
        if self.starts_at is not None and self.ends_at is not None:
            if self.starts_at >= self.ends_at:
                raise ValueError("starts_at должно быть раньше ends_at")
        return self

    def to_command(self) -> CreateQuizCommand:
        return CreateQuizCommand(
            code=str(uuid.uuid4()),
            task_name=self.task_name,
            description=self.description,
            points=self.points,
            week_number=self.week_number,
            starts_at=self.starts_at,
            ends_at=self.ends_at,
            questions=tuple(
                CreateQuizQuestionDTO(
                    question_text=q.question_text,
                    image_url=q.image_url,
                    options=tuple(
                        CreateQuizOptionDTO(
                            option_text=o.option_text,
                            is_correct=o.is_correct,
                            sort_order=o.sort_order,
                        )
                        for o in q.options
                    ),
                )
                for q in self.questions
            ),
        )


# ── Response ──────────────────────────────────────────────────────────────────

class CreatedQuizOptionResponseSchema(BaseModel):
    quiz_question_options_id: int
    option_text: str
    is_correct: bool
    sort_order: int


class CreatedQuizQuestionResponseSchema(BaseModel):
    quiz_questions_id: int
    question_text: str
    image_url: str | None
    options: list[CreatedQuizOptionResponseSchema]


class CreatedQuizResponseSchema(BaseModel):
    tasks_id: int
    code: str
    task_name: str
    questions: list[CreatedQuizQuestionResponseSchema]

    @classmethod
    def from_dto(cls, dto: CreatedQuizDTO) -> "CreatedQuizResponseSchema":
        return cls(
            tasks_id=dto.tasks_id,
            code=dto.code,
            task_name=dto.task_name,
            questions=[
                CreatedQuizQuestionResponseSchema(
                    quiz_questions_id=q.quiz_questions_id,
                    question_text=q.question_text,
                    image_url=q.image_url,
                    options=[
                        CreatedQuizOptionResponseSchema(
                            quiz_question_options_id=o.quiz_question_options_id,
                            option_text=o.option_text,
                            is_correct=o.is_correct,
                            sort_order=o.sort_order,
                        )
                        for o in q.options
                    ],
                )
                for q in dto.questions
            ],
        )
