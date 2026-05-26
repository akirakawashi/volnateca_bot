"""
Seed one dev scenario for manual checks with a real VK account.

Flow:
    1. Clean the dev DB and apply migrations.
    2. Register in the bot from your VK account.
    3. Run one scenario against the created users row. In a clean DB this is
       usually users_id=1.

Examples:
    poetry run python dev_scripts/seed_dev_scenarios.py --scenario week
    poetry run python dev_scripts/seed_dev_scenarios.py --scenario monthly_top
    poetry run python dev_scripts/seed_dev_scenarios.py --scenario project12
    poetry run python dev_scripts/seed_dev_scenarios.py --scenario referral3

Reset only:
    poetry run python dev_scripts/seed_dev_scenarios.py --reset-only
"""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import col

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from domain.enums.achievement import AchievementRepeatPolicy, AchievementType
from domain.enums.task import TaskCompletionStatus, TaskRepeatPolicy, TaskType
from domain.enums.transaction import TransactionSource, TransactionType
from domain.services.level import get_level
from infrastructure.database.models.achievements import Achievement
from infrastructure.database.models.quiz_answers import QuizAnswer
from infrastructure.database.models.quiz_question_options import QuizQuestionOption
from infrastructure.database.models.quiz_questions import QuizQuestion
from infrastructure.database.models.referrals import Referral
from infrastructure.database.models.task_completions import TaskCompletion
from infrastructure.database.models.tasks import Task
from infrastructure.database.models.transactions import Transaction
from infrastructure.database.models.user_achievements import UserAchievement
from infrastructure.database.models.users import User
from settings.factory import ConfigFactory

PROJECT_TZ = ZoneInfo("Europe/Moscow")
REGISTRATION_BONUS_POINTS = 15
REFERRAL_BONUS_POINTS = 30

WEEK_COMPLETION_VK_ID = 900_000_301
REFERRAL_3_INVITER_VK_ID = 900_000_401
REFERRAL_5_INVITER_VK_ID = 900_000_402
REFERRAL_10_INVITER_VK_ID = 900_000_403
REFERRAL_3_NEXT_INVITED_VK_ID = 900_000_491
REFERRAL_5_NEXT_INVITED_VK_ID = 900_000_492
REFERRAL_10_NEXT_INVITED_VK_ID = 900_000_493
MONTHLY_TOP_COMPETITOR_VK_IDS = tuple(range(900_002_001, 900_002_012))

DEV_USER_VK_IDS = {
    WEEK_COMPLETION_VK_ID,
    REFERRAL_3_INVITER_VK_ID,
    REFERRAL_5_INVITER_VK_ID,
    REFERRAL_10_INVITER_VK_ID,
    REFERRAL_3_NEXT_INVITED_VK_ID,
    REFERRAL_5_NEXT_INVITED_VK_ID,
    REFERRAL_10_NEXT_INVITED_VK_ID,
    *MONTHLY_TOP_COMPETITOR_VK_IDS,
    *range(900_001_000, 900_001_009),
    *range(900_001_100, 900_001_104),
    *range(900_001_200, 900_001_209),
}

WEEK_REPOST_CODE = "dev_week12_repost_seeded"
WEEK_LIKE_CODE = "dev_week12_like_to_finish"
WEEK_QUIZ_CODE = "dev_week12_quiz_to_finish"
WEEK_EXTERNAL_ID = "wall-238388485_912001"

DEV_TASK_CODES = (
    WEEK_REPOST_CODE,
    WEEK_LIKE_CODE,
    WEEK_QUIZ_CODE,
)

ACHIEVEMENTS: tuple[dict, ...] = (
    {
        "code": "referral_milestone_3",
        "achievement_name": "Первые друзья",
        "description": "Пригласи 3 друзей и получи бонус",
        "achievement_type": AchievementType.REFERRAL_MILESTONE,
        "repeat_policy": AchievementRepeatPolicy.ONCE,
        "points": 100,
    },
    {
        "code": "referral_milestone_5",
        "achievement_name": "Команда",
        "description": "Пригласи 5 друзей и получи бонус",
        "achievement_type": AchievementType.REFERRAL_MILESTONE,
        "repeat_policy": AchievementRepeatPolicy.ONCE,
        "points": 200,
    },
    {
        "code": "referral_milestone_10",
        "achievement_name": "Амбассадор",
        "description": "Пригласи 10 друзей и получи бонус",
        "achievement_type": AchievementType.REFERRAL_MILESTONE,
        "repeat_policy": AchievementRepeatPolicy.ONCE,
        "points": 400,
    },
    {
        "code": "week_completion",
        "achievement_name": "Все задания недели",
        "description": "Выполни все активные задания недели",
        "achievement_type": AchievementType.WEEK_COMPLETION,
        "repeat_policy": AchievementRepeatPolicy.WEEKLY,
        "points": 100,
    },
    {
        "code": "monthly_top_10",
        "achievement_name": "Топ-10 рейтинга месяца",
        "description": "Попади в топ-10 месячного рейтинга участников",
        "achievement_type": AchievementType.MONTHLY_RATING,
        "repeat_policy": AchievementRepeatPolicy.MONTHLY,
        "points": 250,
    },
    {
        "code": "project_completion_12_weeks",
        "achievement_name": "Все 12 недель",
        "description": "Пройди все 12 недель юбилейного проекта",
        "achievement_type": AchievementType.PROJECT_COMPLETION,
        "repeat_policy": AchievementRepeatPolicy.ONCE,
        "points": 500,
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed one dev scenario for an existing bot user.")
    parser.add_argument(
        "--users-id",
        type=int,
        default=1,
        help="Existing users.users_id to prepare. Default: 1.",
    )
    parser.add_argument(
        "--scenario",
        choices=(
            "week",
            "monthly_top",
            "project12",
            "referral3",
            "referral5",
            "referral10",
        ),
        help="Scenario to seed for the existing target user.",
    )
    parser.add_argument(
        "--post-external-id",
        default=WEEK_EXTERNAL_ID,
        help="Deprecated: kept for compatibility; week scenario now uses a quiz task.",
    )
    parser.add_argument(
        "--reset-only",
        action="store_true",
        help="Delete only dev fixtures created by this script.",
    )
    args = parser.parse_args()
    if not args.reset_only and args.scenario is None:
        parser.error("--scenario is required unless --reset-only is used")
    return args


async def reset_dev_fixtures(session: AsyncSession) -> None:
    user_ids = list(
        await session.scalars(
            select(col(User.users_id)).where(col(User.vk_user_id).in_(DEV_USER_VK_IDS)),
        ),
    )
    task_ids = list(
        await session.scalars(
            select(col(Task.tasks_id)).where(col(Task.code).in_(DEV_TASK_CODES)),
        ),
    )
    question_ids = []
    if task_ids:
        question_ids = list(
            await session.scalars(
                select(col(QuizQuestion.quiz_questions_id)).where(
                    col(QuizQuestion.tasks_id).in_(task_ids),
                ),
            ),
        )

    if user_ids or question_ids:
        conditions = []
        if user_ids:
            conditions.append(col(QuizAnswer.users_id).in_(user_ids))
        if question_ids:
            conditions.append(col(QuizAnswer.quiz_questions_id).in_(question_ids))
        await session.execute(delete(QuizAnswer).where(or_(*conditions)))

    if question_ids:
        await session.execute(
            delete(QuizQuestionOption).where(
                col(QuizQuestionOption.quiz_questions_id).in_(question_ids),
            ),
        )
    if task_ids:
        await session.execute(delete(QuizQuestion).where(col(QuizQuestion.tasks_id).in_(task_ids)))

    if user_ids:
        await session.execute(delete(UserAchievement).where(col(UserAchievement.users_id).in_(user_ids)))
        await session.execute(
            delete(Referral).where(
                or_(
                    col(Referral.inviter_users_id).in_(user_ids),
                    col(Referral.invited_users_id).in_(user_ids),
                ),
            ),
        )

    if user_ids or task_ids:
        conditions = []
        if user_ids:
            conditions.append(col(TaskCompletion.users_id).in_(user_ids))
        if task_ids:
            conditions.append(col(TaskCompletion.tasks_id).in_(task_ids))
        await session.execute(delete(TaskCompletion).where(or_(*conditions)))

    if user_ids or task_ids:
        conditions = []
        if user_ids:
            conditions.append(col(Transaction.users_id).in_(user_ids))
        if task_ids:
            conditions.append(col(Transaction.tasks_id).in_(task_ids))
        await session.execute(delete(Transaction).where(or_(*conditions)))

    if task_ids:
        await session.execute(delete(Task).where(col(Task.tasks_id).in_(task_ids)))
    if user_ids:
        await session.execute(delete(User).where(col(User.users_id).in_(user_ids)))


async def upsert_achievements(session: AsyncSession) -> None:
    for data in ACHIEVEMENTS:
        achievement = await session.scalar(select(Achievement).where(col(Achievement.code) == data["code"]))
        if achievement is None:
            session.add(Achievement(**data, is_active=True))
            continue

        achievement.achievement_name = data["achievement_name"]
        achievement.description = data["description"]
        achievement.achievement_type = data["achievement_type"]
        achievement.repeat_policy = data["repeat_policy"]
        achievement.points = data["points"]
        achievement.is_active = True
        session.add(achievement)
    await session.flush()


async def create_user(session: AsyncSession, *, vk_user_id: int, label: str) -> User:
    user = User(
        vk_user_id=vk_user_id,
        first_name="Dev",
        last_name=label,
        vk_screen_name=f"dev_{vk_user_id}",
        balance_points=REGISTRATION_BONUS_POINTS,
        earned_points_total=REGISTRATION_BONUS_POINTS,
        current_level=get_level(REGISTRATION_BONUS_POINTS),
        is_active=True,
    )
    session.add(user)
    await session.flush()
    await add_transaction(
        session,
        user=user,
        source=TransactionSource.REGISTRATION,
        amount=REGISTRATION_BONUS_POINTS,
        description=f"Dev seed: регистрация {label}",
    )
    return user


async def add_transaction(
    session: AsyncSession,
    *,
    user: User,
    source: TransactionSource,
    amount: int,
    description: str,
    tasks_id: int | None = None,
) -> Transaction:
    if user.users_id is None:
        raise RuntimeError("User primary key was not generated")

    if source != TransactionSource.REGISTRATION:
        balance_before = user.balance_points
        user.balance_points += amount
        user.earned_points_total += amount
        user.current_level = get_level(user.earned_points_total)
        session.add(user)
    else:
        balance_before = 0

    transaction = Transaction(
        users_id=user.users_id,
        tasks_id=tasks_id,
        transaction_type=TransactionType.ACCRUAL,
        transaction_source=source,
        amount=amount,
        balance_before=balance_before,
        balance_after=user.balance_points,
        description=description,
    )
    session.add(transaction)
    await session.flush()
    return transaction


async def create_task(
    session: AsyncSession,
    *,
    code: str,
    task_name: str,
    task_type: TaskType,
    points: int,
    week_number: int | None = None,
    external_id: str | None = None,
    repeat_policy: TaskRepeatPolicy = TaskRepeatPolicy.ONCE,
    is_active: bool = True,
) -> Task:
    now = datetime.now(tz=UTC)
    task = Task(
        code=code,
        task_name=task_name,
        description=f"Dev seed: {task_name}",
        task_type=task_type,
        points=points,
        week_number=week_number,
        external_id=external_id,
        starts_at=now - timedelta(days=1),
        ends_at=now + timedelta(days=30),
        repeat_policy=repeat_policy,
        is_active=is_active,
    )
    session.add(task)
    await session.flush()
    return task


async def create_one_question_quiz(
    session: AsyncSession,
    *,
    code: str,
    task_name: str,
    is_active: bool,
    week_number: int | None = None,
) -> tuple[Task, QuizQuestion, QuizQuestionOption, QuizQuestionOption]:
    task = await create_task(
        session,
        code=code,
        task_name=task_name,
        task_type=TaskType.QUIZ,
        points=15,
        week_number=week_number,
        is_active=is_active,
    )
    if task.tasks_id is None:
        raise RuntimeError("Task primary key was not generated")

    question = QuizQuestion(
        tasks_id=task.tasks_id,
        question_text=f"{task_name}: выбери правильный ответ",
        is_active=True,
    )
    session.add(question)
    await session.flush()
    if question.quiz_questions_id is None:
        raise RuntimeError("Question primary key was not generated")

    wrong_option = QuizQuestionOption(
        quiz_questions_id=question.quiz_questions_id,
        option_text="Неверный ответ",
        is_correct=False,
        sort_order=1,
    )
    correct_option = QuizQuestionOption(
        quiz_questions_id=question.quiz_questions_id,
        option_text="Правильный ответ",
        is_correct=True,
        sort_order=2,
    )
    session.add_all([wrong_option, correct_option])
    await session.flush()
    return task, question, correct_option, wrong_option


async def add_completed_task(
    session: AsyncSession,
    *,
    user: User,
    task: Task,
    checked_at: datetime,
) -> TaskCompletion:
    if user.users_id is None or task.tasks_id is None:
        raise RuntimeError("Required primary key was not generated")

    transaction = await add_transaction(
        session,
        user=user,
        source=TransactionSource.TASK,
        amount=task.points,
        tasks_id=task.tasks_id,
        description=f"Dev seed: выполнено задание {task.code}",
    )
    if transaction.transactions_id is None:
        raise RuntimeError("Transaction primary key was not generated")

    completion = TaskCompletion(
        users_id=user.users_id,
        tasks_id=task.tasks_id,
        completion_key="once",
        transactions_id=transaction.transactions_id,
        task_completion_status=TaskCompletionStatus.COMPLETED,
        points_awarded=task.points,
        external_event_id=f"dev_seed_{task.code}_{user.vk_user_id}",
        evidence_external_id=task.external_id,
        checked_at=checked_at,
    )
    session.add(completion)
    await session.flush()
    return completion


async def answer_completed_quiz(
    session: AsyncSession,
    *,
    user: User,
    task: Task,
    question: QuizQuestion,
    option: QuizQuestionOption,
    checked_at: datetime,
) -> None:
    if user.users_id is None or question.quiz_questions_id is None or option.quiz_question_options_id is None:
        raise RuntimeError("Required primary key was not generated")

    completion = await add_completed_task(session, user=user, task=task, checked_at=checked_at)
    answer = QuizAnswer(
        users_id=user.users_id,
        quiz_questions_id=question.quiz_questions_id,
        quiz_question_options_id=option.quiz_question_options_id,
        is_correct=option.is_correct,
        task_completions_id=completion.task_completions_id,
    )
    session.add(answer)
    await session.flush()
async def seed_week_completion(session: AsyncSession, *, users: dict[int, User]) -> None:
    now = datetime.now(tz=UTC)
    repost_task = await create_task(
        session,
        code=WEEK_REPOST_CODE,
        task_name="Dev week 12 repost already completed",
        task_type=TaskType.VK_REPOST,
        points=20,
        week_number=12,
        external_id=WEEK_EXTERNAL_ID,
    )
    await create_task(
        session,
        code=WEEK_LIKE_CODE,
        task_name="Dev week 12 like to finish",
        task_type=TaskType.VK_LIKE,
        points=10,
        week_number=12,
        external_id=WEEK_EXTERNAL_ID,
    )
    await add_completed_task(
        session,
        user=users[WEEK_COMPLETION_VK_ID],
        task=repost_task,
        checked_at=now - timedelta(hours=1),
    )


async def seed_referrals(session: AsyncSession, *, users: dict[int, User]) -> None:
    await seed_referral_threshold(
        session,
        inviter=users[REFERRAL_3_INVITER_VK_ID],
        prior_invited_vk_ids=range(900_001_000, 900_001_002),
        next_invited=users[REFERRAL_3_NEXT_INVITED_VK_ID],
    )
    await seed_referral_threshold(
        session,
        inviter=users[REFERRAL_5_INVITER_VK_ID],
        prior_invited_vk_ids=range(900_001_100, 900_001_104),
        next_invited=users[REFERRAL_5_NEXT_INVITED_VK_ID],
    )
    await seed_referral_threshold(
        session,
        inviter=users[REFERRAL_10_INVITER_VK_ID],
        prior_invited_vk_ids=range(900_001_200, 900_001_209),
        next_invited=users[REFERRAL_10_NEXT_INVITED_VK_ID],
    )


async def seed_referral_threshold(
    session: AsyncSession,
    *,
    inviter: User,
    prior_invited_vk_ids: range,
    next_invited: User,
) -> None:
    prior_count = 0
    for invited_vk_id in prior_invited_vk_ids:
        invited = await create_user(session, vk_user_id=invited_vk_id, label=f"Referral prior {invited_vk_id}")
        await add_referral(session, inviter=inviter, invited=invited)
        prior_count += 1

    for milestone, code in ((3, "referral_milestone_3"), (5, "referral_milestone_5")):
        if prior_count >= milestone:
            await award_seeded_achievement(
                session,
                user=inviter,
                achievement_code=code,
                achievement_key="once",
                comment=f"Dev seed: referral milestone {milestone} was already awarded",
            )

    print(
        "Referral fixture:",
        f"inviter={inviter.vk_user_id}",
        f"prior={prior_count}",
        f"next_invited={next_invited.vk_user_id}",
    )


async def add_referral(session: AsyncSession, *, inviter: User, invited: User) -> None:
    if inviter.users_id is None or invited.users_id is None:
        raise RuntimeError("User primary key was not generated")

    transaction = await add_transaction(
        session,
        user=inviter,
        source=TransactionSource.REFERRAL,
        amount=REFERRAL_BONUS_POINTS,
        description=f"Dev seed: referral bonus for invited user {invited.vk_user_id}",
    )
    if transaction.transactions_id is None:
        raise RuntimeError("Transaction primary key was not generated")

    session.add(
        Referral(
            inviter_users_id=inviter.users_id,
            invited_users_id=invited.users_id,
            bonus_transactions_id=transaction.transactions_id,
        ),
    )
    await session.flush()


async def award_seeded_achievement(
    session: AsyncSession,
    *,
    user: User,
    achievement_code: str,
    achievement_key: str,
    comment: str,
) -> None:
    if user.users_id is None:
        raise RuntimeError("User primary key was not generated")

    achievement = await session.scalar(select(Achievement).where(col(Achievement.code) == achievement_code))
    if achievement is None or achievement.achievements_id is None:
        raise RuntimeError(f"Achievement {achievement_code!r} was not seeded")

    transaction = await add_transaction(
        session,
        user=user,
        source=TransactionSource.ACHIEVEMENT,
        amount=achievement.points,
        description=f"Dev seed: achievement {achievement_code}",
    )
    if transaction.transactions_id is None:
        raise RuntimeError("Transaction primary key was not generated")

    session.add(
        UserAchievement(
            users_id=user.users_id,
            achievements_id=achievement.achievements_id,
            transactions_id=transaction.transactions_id,
            achievement_key=achievement_key,
            points_awarded=achievement.points,
            comment=comment,
        ),
    )
    await session.flush()


async def seed(session: AsyncSession) -> None:
    await reset_dev_fixtures(session)
    await upsert_achievements(session)

    users = {
        WEEK_COMPLETION_VK_ID: await create_user(
            session,
            vk_user_id=WEEK_COMPLETION_VK_ID,
            label="Week completion",
        ),
        REFERRAL_3_INVITER_VK_ID: await create_user(
            session,
            vk_user_id=REFERRAL_3_INVITER_VK_ID,
            label="Referral 3 inviter",
        ),
        REFERRAL_5_INVITER_VK_ID: await create_user(
            session,
            vk_user_id=REFERRAL_5_INVITER_VK_ID,
            label="Referral 5 inviter",
        ),
        REFERRAL_10_INVITER_VK_ID: await create_user(
            session,
            vk_user_id=REFERRAL_10_INVITER_VK_ID,
            label="Referral 10 inviter",
        ),
        REFERRAL_3_NEXT_INVITED_VK_ID: await create_user(
            session,
            vk_user_id=REFERRAL_3_NEXT_INVITED_VK_ID,
            label="Referral 3 next",
        ),
        REFERRAL_5_NEXT_INVITED_VK_ID: await create_user(
            session,
            vk_user_id=REFERRAL_5_NEXT_INVITED_VK_ID,
            label="Referral 5 next",
        ),
        REFERRAL_10_NEXT_INVITED_VK_ID: await create_user(
            session,
            vk_user_id=REFERRAL_10_NEXT_INVITED_VK_ID,
            label="Referral 10 next",
        ),
    }

    await seed_week_completion(session, users=users)
    await seed_referrals(session, users=users)
    await session.commit()
    return None


def print_report() -> None:
    print("\nSeed complete. Dev users and final actions:")
    print(
        "- Week completion:",
        f"vk_user_id={WEEK_COMPLETION_VK_ID},",
        f"finish LIKE task by external_id={WEEK_EXTERNAL_ID!r}.",
    )
    print(
        "- Referral 3:",
        f"inviter={REFERRAL_3_INVITER_VK_ID}, invited={REFERRAL_3_NEXT_INVITED_VK_ID}.",
    )
    print(
        "- Referral 5:",
        f"inviter={REFERRAL_5_INVITER_VK_ID}, invited={REFERRAL_5_NEXT_INVITED_VK_ID}.",
    )
    print(
        "- Referral 10:",
        f"inviter={REFERRAL_10_INVITER_VK_ID}, invited={REFERRAL_10_NEXT_INVITED_VK_ID}.",
    )


async def get_target_user(session: AsyncSession, *, users_id: int) -> User:
    user = await session.scalar(select(User).where(col(User.users_id) == users_id))
    if user is None:
        raise RuntimeError(
            f"users_id={users_id} не найден. Сначала зарегистрируйся в боте на чистой БД.",
        )
    return user


async def reset_target_dev_fixtures(session: AsyncSession, *, target_user: User) -> None:
    if target_user.users_id is None:
        raise RuntimeError("Target user primary key was not generated")

    task_ids = list(
        await session.scalars(
            select(col(Task.tasks_id)).where(col(Task.code).in_(DEV_TASK_CODES)),
        ),
    )
    question_ids: list[int] = []
    if task_ids:
        question_ids = list(
            await session.scalars(
                select(col(QuizQuestion.quiz_questions_id)).where(col(QuizQuestion.tasks_id).in_(task_ids)),
            ),
        )

    achievement_ids = list(
        await session.scalars(
            select(col(Achievement.achievements_id)).where(
                col(Achievement.code).in_([data["code"] for data in ACHIEVEMENTS]),
            ),
        ),
    )

    transaction_ids_to_delete: set[int] = set()
    if task_ids:
        transaction_ids_to_delete.update(
            await collect_non_null_ints(
                session,
                select(col(TaskCompletion.transactions_id)).where(
                    col(TaskCompletion.users_id) == target_user.users_id,
                    col(TaskCompletion.tasks_id).in_(task_ids),
                    col(TaskCompletion.transactions_id).is_not(None),
                ),
            ),
        )
    if achievement_ids:
        transaction_ids_to_delete.update(
            await collect_non_null_ints(
                session,
                select(col(UserAchievement.transactions_id)).where(
                    col(UserAchievement.users_id) == target_user.users_id,
                    col(UserAchievement.achievements_id).in_(achievement_ids),
                ),
            ),
        )
    transaction_ids_to_delete.update(
        await collect_non_null_ints(
            session,
            select(col(Referral.bonus_transactions_id)).where(
                col(Referral.inviter_users_id) == target_user.users_id,
                col(Referral.bonus_transactions_id).is_not(None),
            ),
        ),
    )

    quiz_answer_conditions = [col(QuizAnswer.users_id) == target_user.users_id]
    if question_ids:
        quiz_answer_conditions.append(col(QuizAnswer.quiz_questions_id).in_(question_ids))
    await session.execute(delete(QuizAnswer).where(or_(*quiz_answer_conditions)))

    if achievement_ids:
        await session.execute(
            delete(UserAchievement).where(
                col(UserAchievement.users_id) == target_user.users_id,
                col(UserAchievement.achievements_id).in_(achievement_ids),
            ),
        )

    await session.execute(
        delete(Referral).where(
            or_(
                col(Referral.inviter_users_id) == target_user.users_id,
                col(Referral.invited_users_id) == target_user.users_id,
            ),
        ),
    )

    if task_ids:
        await session.execute(
            delete(TaskCompletion).where(
                col(TaskCompletion.users_id) == target_user.users_id,
                col(TaskCompletion.tasks_id).in_(task_ids),
            ),
        )

    await session.execute(
        delete(Transaction).where(
            col(Transaction.users_id) == target_user.users_id,
            or_(
                col(Transaction.description).like("Dev seed:%"),
                col(Transaction.transactions_id).in_(transaction_ids_to_delete),
            ),
        ),
    )

    await reset_dev_fixtures(session)
    await recalculate_user_totals(session, user=target_user)
    await session.flush()


async def collect_non_null_ints(session: AsyncSession, statement) -> set[int]:
    values = await session.scalars(statement)
    return {value for value in values if value is not None}


async def recalculate_user_totals(session: AsyncSession, *, user: User) -> None:
    if user.users_id is None:
        raise RuntimeError("User primary key was not generated")

    transactions = list(
        await session.scalars(
            select(Transaction)
            .where(col(Transaction.users_id) == user.users_id)
            .order_by(col(Transaction.transactions_id)),
        ),
    )
    earned = sum(tx.amount for tx in transactions if tx.transaction_type == TransactionType.ACCRUAL)
    spent = sum(tx.amount for tx in transactions if tx.transaction_type == TransactionType.SPEND)

    user.earned_points_total = earned
    user.spent_points_total = spent
    user.balance_points = max(0, earned - spent)
    user.current_level = get_level(earned)
    session.add(user)


async def seed_target_week_completion(
    session: AsyncSession,
    *,
    user: User,
) -> list[str]:
    current_task, current_question, current_correct_option, _ = await create_one_question_quiz(
        session,
        code=WEEK_QUIZ_CODE,
        task_name="Dev week 12 quiz to finish",
        is_active=True,
        week_number=12,
    )
    if current_task.tasks_id is None:
        raise RuntimeError("Week quiz task primary key was not generated")
    if current_question.quiz_questions_id is None or current_correct_option.quiz_question_options_id is None:
        raise RuntimeError("Week quiz fixture primary keys were not generated")

    return [
        f"Prepared vk_user_id={user.vk_user_id} for week_completion week 12.",
        f"Current weekly quiz tasks_id={current_task.tasks_id}.",
        f"Direct answer payload: quiz_questions_id={current_question.quiz_questions_id}, "
        f"option_id={current_correct_option.quiz_question_options_id}.",
        "Next action: open tasks in the bot, start the weekly quiz, choose 'Правильный ответ'.",
        "Expected: quiz task +15 and then week_completion +100.",
    ]


async def seed_target_monthly_top(session: AsyncSession, *, user: User) -> list[str]:
    month = datetime.now(PROJECT_TZ).strftime("%Y-%m")
    competitor_amounts = (1200, 1100, 1000, 900, 800, 700, 600, 500, 400, 50, 25)

    for index, (vk_user_id, amount) in enumerate(
        zip(MONTHLY_TOP_COMPETITOR_VK_IDS, competitor_amounts, strict=True),
        start=1,
    ):
        competitor = await create_user(
            session,
            vk_user_id=vk_user_id,
            label=f"Monthly top competitor {index}",
        )
        await add_transaction(
            session,
            user=competitor,
            source=TransactionSource.ADJUSTMENT,
            amount=amount,
            description=f"Dev seed: monthly_top_10 competitor score {index}",
        )

    await add_transaction(
        session,
        user=user,
        source=TransactionSource.ADJUSTMENT,
        amount=10_000,
        description="Dev seed: monthly_top_10 target score",
    )

    return [
        f"Prepared vk_user_id={user.vk_user_id} for monthly_top_10 in {month}.",
        f"Next action: poetry run python dev_scripts/award_monthly_top.py --month {month}",
        "Expected: target user is printed in top winners with status=awarded and +250.",
        "Repeat the same command to check idempotency: status should become already_awarded.",
    ]


async def seed_target_project_completion(session: AsyncSession, *, user: User) -> list[str]:
    for week_number in range(1, 12):
        await award_seeded_achievement(
            session,
            user=user,
            achievement_code="week_completion",
            achievement_key=f"week_{week_number:02d}",
            comment=f"Dev seed: week {week_number} already completed before final project check",
        )

    current_task, current_question, current_correct_option, _ = await create_one_question_quiz(
        session,
        code=WEEK_QUIZ_CODE,
        task_name="Dev week 12 quiz to finish project",
        is_active=True,
        week_number=12,
    )
    if current_task.tasks_id is None:
        raise RuntimeError("Project completion quiz task primary key was not generated")
    if current_question.quiz_questions_id is None or current_correct_option.quiz_question_options_id is None:
        raise RuntimeError("Project completion quiz fixture primary keys were not generated")

    return [
        f"Prepared vk_user_id={user.vk_user_id} with week_completion week_01..week_11.",
        f"Current weekly quiz tasks_id={current_task.tasks_id}.",
        f"Direct answer payload: quiz_questions_id={current_question.quiz_questions_id}, "
        f"option_id={current_correct_option.quiz_question_options_id}.",
        "Next action: open tasks in the bot, start the weekly quiz, choose 'Правильный ответ'.",
        "Expected: quiz +15, week_completion week 12 +100, project_completion_12_weeks +500.",
    ]


async def seed_target_referral_threshold(
    session: AsyncSession,
    *,
    user: User,
    threshold: int,
    group_id: int,
) -> list[str]:
    prior_count = threshold - 1
    for index in range(prior_count):
        invited = await create_user(
            session,
            vk_user_id=900_001_000 + index,
            label=f"Referral prior {index + 1}",
        )
        await add_referral(session, inviter=user, invited=invited)

    if threshold > 3:
        await award_seeded_achievement(
            session,
            user=user,
            achievement_code="referral_milestone_3",
            achievement_key="once",
            comment="Dev seed: referral milestone 3 already awarded",
        )
    if threshold > 5:
        await award_seeded_achievement(
            session,
            user=user,
            achievement_code="referral_milestone_5",
            achievement_key="once",
            comment="Dev seed: referral milestone 5 already awarded",
        )

    link = f"https://vk.com/write-{group_id}?ref={user.vk_user_id}"
    return [
        f"Prepared vk_user_id={user.vk_user_id} as inviter with {prior_count} prior referrals.",
        f"Referral link for the next new account: {link}",
        "Next action: register one more VK account through this ref link.",
        f"Expected: referral +30 and referral_milestone_{threshold} bonus.",
    ]


async def seed_target_scenario(
    session: AsyncSession,
    *,
    user: User,
    scenario: str,
    group_id: int,
    post_external_id: str,
) -> list[str]:
    await reset_target_dev_fixtures(session, target_user=user)

    if scenario == "week":
        lines = await seed_target_week_completion(session, user=user)
    elif scenario == "monthly_top":
        lines = await seed_target_monthly_top(session, user=user)
    elif scenario == "project12":
        lines = await seed_target_project_completion(session, user=user)
    elif scenario == "referral3":
        lines = await seed_target_referral_threshold(session, user=user, threshold=3, group_id=group_id)
    elif scenario == "referral5":
        lines = await seed_target_referral_threshold(session, user=user, threshold=5, group_id=group_id)
    elif scenario == "referral10":
        lines = await seed_target_referral_threshold(session, user=user, threshold=10, group_id=group_id)
    else:
        raise ValueError(f"Unsupported scenario: {scenario}")

    await session.commit()
    return lines


async def main() -> None:
    args = parse_args()
    cfg = ConfigFactory()
    engine = create_async_engine(cfg.db.dsn(), echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with async_session() as session:
            user = await get_target_user(session, users_id=args.users_id)
            if args.reset_only:
                await reset_target_dev_fixtures(session, target_user=user)
                await session.commit()
                print(f"Dev fixtures removed for users_id={args.users_id}, vk_user_id={user.vk_user_id}.")
                return

            lines = await seed_target_scenario(
                session,
                user=user,
                scenario=args.scenario,
                group_id=cfg.vk.GROUP_ID,
                post_external_id=args.post_external_id,
            )

        print("\nSeed complete.")
        for line in lines:
            print(f"- {line}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
