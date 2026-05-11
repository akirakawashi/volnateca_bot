from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class ProcessReferralDTO:
    created: bool
    inviter_vk_user_id: int
    inviter_users_id: int | None
    bonus_points: int
    inviter_balance_points: int | None
    milestone_reached: int | None
    milestone_bonus_points: int | None
    level_up: int | None = None  # новый уровень инвайтера, если произошёл апгрейд


__all__ = ["ProcessReferralDTO"]
