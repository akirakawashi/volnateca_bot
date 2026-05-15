from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from zoneinfo import ZoneInfo

from application.base_interactor import Interactor
from application.interface.repositories.achievements import IAchievementRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.uow import IUnitOfWork
from application.services.award_achievement_service import (
    AchievementAwardSpec,
    AwardAchievementOutcomeStatus,
    AwardAchievementService,
)

MONTHLY_TOP_ACHIEVEMENT_CODE = "monthly_top_10"


class MonthlyTopAwardStatus(str, Enum):
    AWARDED = "awarded"
    ALREADY_AWARDED = "already_awarded"
    USER_NOT_REGISTERED = "user_not_registered"


@dataclass(slots=True, frozen=True, kw_only=True)
class AwardMonthlyTopCommand:
    month: str
    limit: int = 10


@dataclass(slots=True, frozen=True, kw_only=True)
class MonthlyTopAward:
    rank: int
    users_id: int
    vk_user_id: int
    monthly_points: int
    status: MonthlyTopAwardStatus
    points_awarded: int
    balance_points: int | None
    level_up: int | None


@dataclass(slots=True, frozen=True, kw_only=True)
class AwardMonthlyTopDTO:
    month: str
    period_start_at: datetime
    period_end_at: datetime
    achievement_found: bool
    awards: tuple[MonthlyTopAward, ...]


class AwardMonthlyTopHandler(Interactor[AwardMonthlyTopCommand, AwardMonthlyTopDTO]):
    """Начисляет достижение пользователям из топа начислений за месяц."""

    def __init__(
        self,
        transaction_repository: ITransactionRepository,
        achievement_repository: IAchievementRepository,
        award_achievement_service: AwardAchievementService,
        uow: IUnitOfWork,
        project_timezone: ZoneInfo,
    ) -> None:
        self.transaction_repository = transaction_repository
        self.achievement_repository = achievement_repository
        self.award_achievement_service = award_achievement_service
        self.uow = uow
        self.project_timezone = project_timezone

    async def __call__(self, command_data: AwardMonthlyTopCommand) -> AwardMonthlyTopDTO:
        if command_data.limit < 1:
            raise ValueError("Лимит должен быть положительным")

        month = parse_month_key(command_data.month)
        period_start_at, period_end_at = build_month_period(
            month=month,
            project_timezone=self.project_timezone,
        )

        achievement = await self.achievement_repository.get_by_code(code=MONTHLY_TOP_ACHIEVEMENT_CODE)
        if achievement is None:
            return AwardMonthlyTopDTO(
                month=month,
                period_start_at=period_start_at,
                period_end_at=period_end_at,
                achievement_found=False,
                awards=(),
            )

        top_users = await self.transaction_repository.list_top_accrual_users_for_period(
            start_at=period_start_at,
            end_at=period_end_at,
            limit=command_data.limit,
            excluded_achievement_code=MONTHLY_TOP_ACHIEVEMENT_CODE,
        )

        awards: list[MonthlyTopAward] = []
        for rank, top_user in enumerate(top_users, start=1):
            outcome = await self.award_achievement_service.award(
                vk_user_id=top_user.vk_user_id,
                achievement=AchievementAwardSpec(
                    achievements_id=achievement.achievements_id,
                    achievement_name=achievement.achievement_name,
                    points=achievement.points,
                ),
                achievement_key=month,
            )
            awards.append(
                MonthlyTopAward(
                    rank=rank,
                    users_id=top_user.users_id,
                    vk_user_id=top_user.vk_user_id,
                    monthly_points=top_user.points,
                    status=map_award_status(outcome.status),
                    points_awarded=outcome.points_awarded,
                    balance_points=outcome.balance_points,
                    level_up=outcome.level_up,
                ),
            )

        await self.uow.commit()
        return AwardMonthlyTopDTO(
            month=month,
            period_start_at=period_start_at,
            period_end_at=period_end_at,
            achievement_found=True,
            awards=tuple(awards),
        )


def parse_month_key(month: str) -> str:
    try:
        parsed = datetime.strptime(month, "%Y-%m")  # noqa: DTZ007
    except ValueError as exc:
        raise ValueError("Месяц должен быть в формате YYYY-MM") from exc
    return f"{parsed.year:04d}-{parsed.month:02d}"


def build_month_period(*, month: str, project_timezone: ZoneInfo) -> tuple[datetime, datetime]:
    year, month_number = (int(part) for part in month.split("-", maxsplit=1))
    start_local = datetime(year, month_number, 1, tzinfo=project_timezone)
    if month_number == 12:
        end_local = datetime(year + 1, 1, 1, tzinfo=project_timezone)
    else:
        end_local = datetime(year, month_number + 1, 1, tzinfo=project_timezone)
    return start_local.astimezone(UTC), end_local.astimezone(UTC)


def map_award_status(status: AwardAchievementOutcomeStatus) -> MonthlyTopAwardStatus:
    match status:
        case AwardAchievementOutcomeStatus.COMPLETED:
            return MonthlyTopAwardStatus.AWARDED
        case AwardAchievementOutcomeStatus.ALREADY_AWARDED:
            return MonthlyTopAwardStatus.ALREADY_AWARDED
        case AwardAchievementOutcomeStatus.USER_NOT_REGISTERED:
            return MonthlyTopAwardStatus.USER_NOT_REGISTERED
    raise ValueError(f"Неизвестный статус выдачи достижения: {status}")


__all__ = [
    "MONTHLY_TOP_ACHIEVEMENT_CODE",
    "AwardMonthlyTopCommand",
    "AwardMonthlyTopDTO",
    "AwardMonthlyTopHandler",
    "MonthlyTopAward",
    "MonthlyTopAwardStatus",
    "build_month_period",
    "parse_month_key",
]
