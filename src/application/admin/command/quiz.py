from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateQuizOptionDTO:
    option_text: str
    is_correct: bool
    sort_order: int


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateQuizQuestionDTO:
    question_text: str
    image_attachment: str | None
    options: tuple[CreateQuizOptionDTO, ...]


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateQuizCommand:
    code: str
    task_name: str
    description: str | None
    points: int
    week_number: int | None
    starts_at: datetime | None
    ends_at: datetime | None
    questions: tuple[CreateQuizQuestionDTO, ...]


__all__ = [
    "CreateQuizCommand",
    "CreateQuizOptionDTO",
    "CreateQuizQuestionDTO",
]
