from dataclasses import dataclass

from application.base_interactor import Interactor
from application.common.dto.referral import ProcessReferralDTO
from application.interface.repositories.achievements import IAchievementRepository
from application.interface.repositories.referrals import IReferralRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository
from application.interface.uow import IUnitOfWork
from application.services.award_achievement_service import (
    AchievementAwardSpec,
    AwardAchievementOutcomeStatus,
    AwardAchievementService,
)
from domain.enums.transaction import TransactionSource, TransactionType
from domain.services.level import get_level
from domain.services.wallet import WalletService

REFERRAL_BONUS_POINTS = 30

# Пороговые достижения: количество рефералов → код достижения в таблице achievements
REFERRAL_MILESTONES: dict[int, str] = {
    3: "referral_milestone_3",
    5: "referral_milestone_5",
    10: "referral_milestone_10",
}


@dataclass(slots=True, frozen=True, kw_only=True)
class ProcessReferralCommand:
    invited_vk_user_id: int
    inviter_vk_user_id: int


class ProcessReferralHandler(Interactor[ProcessReferralCommand, ProcessReferralDTO]):
    """Обрабатывает реферальную связь при регистрации нового пользователя.

    Начисляет +30 ✦ пригласившему, проверяет достижение порога (3/5/10 рефералов)
    и при необходимости начисляет milestone-бонус.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        referral_repository: IReferralRepository,
        achievement_repository: IAchievementRepository,
        transaction_repository: ITransactionRepository,
        award_achievement_service: AwardAchievementService,
        uow: IUnitOfWork,
    ) -> None:
        self.user_repository = user_repository
        self.referral_repository = referral_repository
        self.achievement_repository = achievement_repository
        self.transaction_repository = transaction_repository
        self.award_achievement_service = award_achievement_service
        self.uow = uow

    async def __call__(self, command_data: ProcessReferralCommand) -> ProcessReferralDTO:
        if command_data.invited_vk_user_id == command_data.inviter_vk_user_id:
            return self._no_op(inviter_vk_user_id=command_data.inviter_vk_user_id)

        inviter = await self.user_repository.get_by_vk_user_id(
            vk_user_id=command_data.inviter_vk_user_id,
        )
        if inviter is None:
            return self._no_op(inviter_vk_user_id=command_data.inviter_vk_user_id)

        invited = await self.user_repository.get_by_vk_user_id(
            vk_user_id=command_data.invited_vk_user_id,
        )
        if invited is None:
            return self._no_op(
                inviter_vk_user_id=command_data.inviter_vk_user_id,
                inviter_users_id=inviter.users_id,
            )

        # Создаём реферальную связь (идемпотентно)
        referrals_id, created = await self.referral_repository.create_if_not_exists(
            inviter_users_id=inviter.users_id,
            invited_users_id=invited.users_id,
        )
        if not created:
            await self.uow.commit()
            return self._no_op(
                inviter_vk_user_id=command_data.inviter_vk_user_id,
                inviter_users_id=inviter.users_id,
            )

        # Блокируем строку баланса инвайтера на время транзакции
        snapshot = await self.user_repository.get_balance_snapshot_for_update(
            vk_user_id=command_data.inviter_vk_user_id,
        )
        if snapshot is None:
            await self.uow.commit()
            return ProcessReferralDTO(
                created=True,
                inviter_vk_user_id=command_data.inviter_vk_user_id,
                inviter_users_id=inviter.users_id,
                bonus_points=0,
                inviter_balance_points=None,
                milestone_reached=None,
                milestone_bonus_points=None,
            )

        # Начисляем реферальный бонус
        accrual = WalletService.accrue(
            balance_before=snapshot.balance_points,
            earned_points_total_before=snapshot.earned_points_total,
            amount=REFERRAL_BONUS_POINTS,
        )
        await self.user_repository.apply_balance_change(
            users_id=snapshot.users_id,
            balance_points=accrual.balance_after,
            earned_points_total=accrual.earned_points_total_after,
            current_level=get_level(accrual.earned_points_total_after),
        )
        referral_transaction = await self.transaction_repository.create(
            users_id=snapshot.users_id,
            tasks_id=None,
            prizes_id=None,
            transaction_type=TransactionType.ACCRUAL,
            transaction_source=TransactionSource.REFERRAL,
            amount=accrual.amount,
            balance_before=accrual.balance_before,
            balance_after=accrual.balance_after,
            description="Бонус за приглашённого друга",
        )
        await self.referral_repository.set_bonus_transaction(
            referrals_id=referrals_id,
            transactions_id=referral_transaction.transactions_id,
        )

        # Проверяем milestone-пороги
        milestone_reached: int | None = None
        milestone_bonus_points: int | None = None
        current_balance = accrual.balance_after
        current_earned = accrual.earned_points_total_after

        referral_count = await self.referral_repository.count_referrals(
            inviter_users_id=inviter.users_id,
        )
        milestone_code = REFERRAL_MILESTONES.get(referral_count)
        if milestone_code is not None:
            achievement = await self.achievement_repository.get_by_code(code=milestone_code)
            if achievement is not None:
                achievement_outcome = await self.award_achievement_service.award(
                    vk_user_id=command_data.inviter_vk_user_id,
                    achievement=AchievementAwardSpec(
                        achievements_id=achievement.achievements_id,
                        achievement_name=achievement.achievement_name,
                        points=achievement.points,
                    ),
                    achievement_key="once",
                )
                if achievement_outcome.status == AwardAchievementOutcomeStatus.COMPLETED:
                    milestone_reached = referral_count
                    milestone_bonus_points = achievement_outcome.points_awarded
                    if achievement_outcome.balance_points is not None:
                        current_balance = achievement_outcome.balance_points
                    current_earned += achievement_outcome.points_awarded

        # Итоговый level_up — сравниваем начальный уровень с финальным
        # (учитывает как реферальный бонус, так и возможный milestone-бонус)
        level_before = get_level(snapshot.earned_points_total)
        final_level = get_level(current_earned)
        level_up: int | None = final_level if final_level > level_before else None

        await self.uow.commit()
        return ProcessReferralDTO(
            created=True,
            inviter_vk_user_id=command_data.inviter_vk_user_id,
            inviter_users_id=inviter.users_id,
            bonus_points=REFERRAL_BONUS_POINTS,
            inviter_balance_points=current_balance,
            milestone_reached=milestone_reached,
            milestone_bonus_points=milestone_bonus_points,
            level_up=level_up,
        )

    @staticmethod
    def _no_op(
        *,
        inviter_vk_user_id: int,
        inviter_users_id: int | None = None,
    ) -> ProcessReferralDTO:
        return ProcessReferralDTO(
            created=False,
            inviter_vk_user_id=inviter_vk_user_id,
            inviter_users_id=inviter_users_id,
            bonus_points=0,
            inviter_balance_points=None,
            milestone_reached=None,
            milestone_bonus_points=None,
        )
