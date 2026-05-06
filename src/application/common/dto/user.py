from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class VKUserRegistrationDTO:
    users_id: int
    vk_user_id: int
    balance_points: int
    created: bool
