from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class QuizQuestionOptionDTO:
    quiz_question_options_id: int
    option_text: str


@dataclass(slots=True, frozen=True, kw_only=True)
class QuizQuestionDTO:
    quiz_questions_id: int
    question_text: str
    image_url: str | None
    question_number: int
    total_questions: int
    options: tuple[QuizQuestionOptionDTO, ...]


@dataclass(slots=True, frozen=True, kw_only=True)
class QuizAnswerSavedDTO:
    is_correct: bool
    correct_option_text: str
    tasks_id: int
    already_answered: bool
    quiz_answers_id: int | None = None


__all__ = ["QuizAnswerSavedDTO", "QuizQuestionDTO", "QuizQuestionOptionDTO"]
