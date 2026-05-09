from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class UserBalanceSnapshot:
    """Снимок баланса пользователя на момент SELECT ... FOR UPDATE.

    Используется оркестраторами (например, AwardTaskService) для расчёта
    нового состояния через WalletService без необходимости держать ORM-сущность
    выше слоя репозитория.
    """

    users_id: int
    vk_user_id: int
    balance_points: int
    earned_points_total: int
