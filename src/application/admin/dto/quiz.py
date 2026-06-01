from dataclasses import dataclass


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


__all__ = [
    "CreatedQuizDTO",
    "CreatedQuizOptionDTO",
    "CreatedQuizQuestionDTO",
]
