from dataclasses import dataclass
from enum import Enum

from application.interface.repositories.achievements import IAchievementRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository
from domain.enums.transaction import TransactionSource, TransactionType
from domain.services.level import get_level
from domain.services.wallet import WalletService


class AwardAchievementOutcomeStatus(str, Enum):
    """Статус попытки выдать достижение пользователю."""

    COMPLETED = "completed"
    ALREADY_AWARDED = "already_awarded"
    USER_NOT_REGISTERED = "user_not_registered"


@dataclass(slots=True, frozen=True, kw_only=True)
class AchievementAwardSpec:
    """Описание достижения, за которое нужно начислить очки."""

    achievements_id: int
    achievement_name: str
    points: int


@dataclass(slots=True, frozen=True, kw_only=True)
class AwardAchievementOutcome:
    """Результат AwardAchievementService.award."""

    status: AwardAchievementOutcomeStatus
    vk_user_id: int
    users_id: int | None = None
    achievements_id: int | None = None
    achievement_name: str | None = None
    transactions_id: int | None = None
    achievement_key: str | None = None
    points_awarded: int = 0
    balance_points: int | None = None
    level_up: int | None = None


class AwardAchievementService:
    """Единое место для выдачи достижений и бонусных правил.

    Сервис повторяет контракт AwardTaskService, но работает с таблицей
    user_achievements: проверяет идемпотентность по achievement_key,
    начисляет очки, пишет транзакцию и фиксирует факт выдачи достижения.
    """

    def __init__(
        self,
        users: IUserRepository,
        achievements: IAchievementRepository,
        transactions: ITransactionRepository,
    ) -> None:
        self._users = users
        self._achievements = achievements
        self._transactions = transactions

    async def award(
        self,
        *,
        vk_user_id: int,
        achievement: AchievementAwardSpec,
        achievement_key: str,
    ) -> AwardAchievementOutcome:
        snapshot = await self._users.get_balance_snapshot_for_update(vk_user_id=vk_user_id)
        if snapshot is None:
            return AwardAchievementOutcome(
                status=AwardAchievementOutcomeStatus.USER_NOT_REGISTERED,
                vk_user_id=vk_user_id,
                achievements_id=achievement.achievements_id,
                achievement_name=achievement.achievement_name,
                achievement_key=achievement_key,
            )

        if await self._achievements.is_awarded(
            users_id=snapshot.users_id,
            achievements_id=achievement.achievements_id,
            achievement_key=achievement_key,
        ):
            return AwardAchievementOutcome(
                status=AwardAchievementOutcomeStatus.ALREADY_AWARDED,
                vk_user_id=vk_user_id,
                users_id=snapshot.users_id,
                achievements_id=achievement.achievements_id,
                achievement_name=achievement.achievement_name,
                achievement_key=achievement_key,
                balance_points=snapshot.balance_points,
            )

        accrual = WalletService.accrue(
            balance_before=snapshot.balance_points,
            earned_points_total_before=snapshot.earned_points_total,
            amount=achievement.points,
        )

        level_before = get_level(snapshot.earned_points_total)
        level_after = get_level(accrual.earned_points_total_after)
        level_up = level_after if level_after > level_before else None

        await self._users.apply_balance_change(
            users_id=snapshot.users_id,
            balance_points=accrual.balance_after,
            earned_points_total=accrual.earned_points_total_after,
            current_level=level_after,
        )

        transaction = await self._transactions.create(
            users_id=snapshot.users_id,
            tasks_id=None,
            prizes_id=None,
            transaction_type=TransactionType.ACCRUAL,
            transaction_source=TransactionSource.ACHIEVEMENT,
            amount=accrual.amount,
            balance_before=accrual.balance_before,
            balance_after=accrual.balance_after,
            description=f"Достижение: {achievement.achievement_name}",
        )

        awarded = await self._achievements.award_if_not_exists(
            users_id=snapshot.users_id,
            achievements_id=achievement.achievements_id,
            transactions_id=transaction.transactions_id,
            achievement_key=achievement_key,
            points=achievement.points,
        )
        if not awarded:
            raise RuntimeError("Достижение стало дубликатом после начисления")

        return AwardAchievementOutcome(
            status=AwardAchievementOutcomeStatus.COMPLETED,
            vk_user_id=vk_user_id,
            users_id=snapshot.users_id,
            achievements_id=achievement.achievements_id,
            achievement_name=achievement.achievement_name,
            transactions_id=transaction.transactions_id,
            achievement_key=achievement_key,
            points_awarded=accrual.amount,
            balance_points=accrual.balance_after,
            level_up=level_up,
        )


__all__ = [
    "AchievementAwardSpec",
    "AwardAchievementOutcome",
    "AwardAchievementOutcomeStatus",
    "AwardAchievementService",
]
