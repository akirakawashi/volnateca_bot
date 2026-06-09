from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True, kw_only=True)
class CreatedQuizOptionDTO:
    quiz_question_options_id: int
    option_text: str
    is_correct: bool
    sort_order: int


@dataclass(slots=True, frozen=True, kw_only=True)
class CreatedQuizQuestionDTO:
    quiz_questions_id: int
    question_text: str
    image_attachment: str | None
    options: tuple[CreatedQuizOptionDTO, ...]


@dataclass(slots=True, frozen=True, kw_only=True)
class CreatedQuizDTO:
    tasks_id: int
    code: str
    task_name: str
    questions: tuple[CreatedQuizQuestionDTO, ...]


@dataclass(slots=True, frozen=True, kw_only=True)
class QuizQuestionImageAdminDTO:
    quiz_questions_id: int
    question_text: str
    image_attachment: str | None


@dataclass(slots=True, frozen=True, kw_only=True)
class QuizAdminDTO:
    tasks_id: int
    code: str
    task_name: str
    starts_at: datetime | None
    ends_at: datetime | None
    can_edit: bool
    questions: tuple[QuizQuestionImageAdminDTO, ...]


__all__ = [
    "CreatedQuizDTO",
    "CreatedQuizOptionDTO",
    "CreatedQuizQuestionDTO",
    "QuizAdminDTO",
    "QuizQuestionImageAdminDTO",
]
