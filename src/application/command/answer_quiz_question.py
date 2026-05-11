from dataclasses import dataclass
from datetime import UTC, datetime

from application.base_interactor import Interactor
from application.common.dto.quiz import QuizQuestionDTO
from application.interface.repositories.quiz import IQuizRepository
from application.interface.repositories.tasks import ITaskRepository
from application.interface.uow import IUnitOfWork
from application.services.award_task_service import (
    AwardTaskOutcomeStatus,
    AwardTaskService,
    TaskAwardSpec,
)
from application.services.quiz_streak_achievement_service import QuizStreakAchievementService
from application.services.task_completion_key import build_task_completion_key


@dataclass(slots=True, frozen=True, kw_only=True)
class AnswerQuizQuestionCommand:
    vk_user_id: int
    quiz_questions_id: int
    quiz_question_options_id: int


@dataclass(slots=True, frozen=True, kw_only=True)
class AnswerQuizQuestionDTO:
    is_correct: bool
    correct_option_text: str
    next_question: QuizQuestionDTO | None
    task_completed: bool
    points_awarded: int
    balance_points: int | None
    level_up: int | None
    week_completion_week_number: int | None
    week_completion_points_awarded: int
    week_completion_balance_points: int | None
    week_completion_level_up: int | None
    quiz_streak_count: int | None
    quiz_streak_points_awarded: int
    quiz_streak_balance_points: int | None
    quiz_streak_level_up: int | None
    already_answered: bool
    invalid_payload: bool
    quiz_unavailable: bool


class AnswerQuizQuestionHandler(
    Interactor[AnswerQuizQuestionCommand, AnswerQuizQuestionDTO],
):
    """Сохраняет ответ пользователя на вопрос квиза.

    Если все вопросы задания отвечены, начисляет награду через AwardTaskService.
    """

    def __init__(
        self,
        quiz_repository: IQuizRepository,
        task_repository: ITaskRepository,
        award_service: AwardTaskService,
        quiz_streak_achievement_service: QuizStreakAchievementService,
        uow: IUnitOfWork,
    ) -> None:
        self.quiz_repository = quiz_repository
        self.task_repository = task_repository
        self.award_service = award_service
        self.quiz_streak_achievement_service = quiz_streak_achievement_service
        self.uow = uow

    async def __call__(
        self,
        command_data: AnswerQuizQuestionCommand,
    ) -> AnswerQuizQuestionDTO:
        saved = await self.quiz_repository.save_answer(
            vk_user_id=command_data.vk_user_id,
            quiz_questions_id=command_data.quiz_questions_id,
            quiz_question_options_id=command_data.quiz_question_options_id,
        )

        if saved is None:
            return AnswerQuizQuestionDTO(
                is_correct=False,
                correct_option_text="",
                next_question=None,
                task_completed=False,
                points_awarded=0,
                balance_points=None,
                level_up=None,
                week_completion_week_number=None,
                week_completion_points_awarded=0,
                week_completion_balance_points=None,
                week_completion_level_up=None,
                quiz_streak_count=None,
                quiz_streak_points_awarded=0,
                quiz_streak_balance_points=None,
                quiz_streak_level_up=None,
                already_answered=False,
                invalid_payload=True,
                quiz_unavailable=False,
            )

        if saved.quiz_unavailable:
            return AnswerQuizQuestionDTO(
                is_correct=False,
                correct_option_text="",
                next_question=None,
                task_completed=False,
                points_awarded=0,
                balance_points=None,
                level_up=None,
                week_completion_week_number=None,
                week_completion_points_awarded=0,
                week_completion_balance_points=None,
                week_completion_level_up=None,
                quiz_streak_count=None,
                quiz_streak_points_awarded=0,
                quiz_streak_balance_points=None,
                quiz_streak_level_up=None,
                already_answered=False,
                invalid_payload=False,
                quiz_unavailable=True,
            )

        task_completed = False
        points_awarded = 0
        balance_points: int | None = None
        level_up: int | None = None
        week_completion_week_number: int | None = None
        week_completion_points_awarded = 0
        week_completion_balance_points: int | None = None
        week_completion_level_up: int | None = None
        quiz_streak_count: int | None = None
        quiz_streak_points_awarded = 0
        quiz_streak_balance_points: int | None = None
        quiz_streak_level_up: int | None = None

        if not saved.already_answered:
            remaining = await self.quiz_repository.get_remaining_questions_count(
                tasks_id=saved.tasks_id,
                vk_user_id=command_data.vk_user_id,
            )

            if remaining == 0:
                task_spec = await self.task_repository.get_task_for_award(
                    tasks_id=saved.tasks_id,
                )
                if task_spec is not None:
                    completion_key = build_task_completion_key(
                        repeat_policy=task_spec.repeat_policy,
                        week_number=task_spec.week_number,
                        checked_at=datetime.now(tz=UTC),
                    )
                    outcome = await self.award_service.award(
                        vk_user_id=command_data.vk_user_id,
                        task=TaskAwardSpec(
                            tasks_id=task_spec.tasks_id,
                            task_name=task_spec.task_name,
                            points=task_spec.points,
                            week_number=task_spec.week_number,
                        ),
                        completion_key=completion_key,
                        event_id=None,
                        evidence_external_id=None,
                    )
                    if outcome.status in (
                        AwardTaskOutcomeStatus.COMPLETED,
                        AwardTaskOutcomeStatus.ALREADY_COMPLETED,
                    ):
                        task_completed = True
                        points_awarded = outcome.points_awarded
                        balance_points = outcome.balance_points
                        level_up = outcome.level_up
                        week_completion_week_number = outcome.week_completion_week_number
                        week_completion_points_awarded = outcome.week_completion_points_awarded
                        week_completion_balance_points = outcome.week_completion_balance_points
                        week_completion_level_up = outcome.week_completion_level_up
                        if outcome.task_completions_id is not None and saved.quiz_answers_id is not None:
                            await self.quiz_repository.link_answer_to_task_completion(
                                quiz_answers_id=saved.quiz_answers_id,
                                task_completions_id=outcome.task_completions_id,
                            )
                        if outcome.status == AwardTaskOutcomeStatus.COMPLETED:
                            quiz_streak_award = await self.quiz_streak_achievement_service.award_if_needed(
                                vk_user_id=command_data.vk_user_id,
                            )
                            if quiz_streak_award is not None:
                                quiz_streak_count = quiz_streak_award.streak_count
                                quiz_streak_points_awarded = quiz_streak_award.points_awarded
                                quiz_streak_balance_points = quiz_streak_award.balance_points
                                quiz_streak_level_up = quiz_streak_award.level_up

        await self.uow.commit()

        next_question: QuizQuestionDTO | None = None
        if not task_completed:
            next_question = await self.quiz_repository.get_first_unanswered_question(
                tasks_id=saved.tasks_id,
                vk_user_id=command_data.vk_user_id,
            )

        return AnswerQuizQuestionDTO(
            is_correct=saved.is_correct,
            correct_option_text=saved.correct_option_text,
            next_question=next_question,
            task_completed=task_completed,
            points_awarded=points_awarded,
            balance_points=balance_points,
            level_up=level_up,
            week_completion_week_number=week_completion_week_number,
            week_completion_points_awarded=week_completion_points_awarded,
            week_completion_balance_points=week_completion_balance_points,
            week_completion_level_up=week_completion_level_up,
            quiz_streak_count=quiz_streak_count,
            quiz_streak_points_awarded=quiz_streak_points_awarded,
            quiz_streak_balance_points=quiz_streak_balance_points,
            quiz_streak_level_up=quiz_streak_level_up,
            already_answered=saved.already_answered,
            invalid_payload=False,
            quiz_unavailable=False,
        )
