from dataclasses import dataclass
from enum import Enum


class UserMessageIntent(str, Enum):
    BALANCE = "balance"
    TASKS = "tasks"
    SHOP = "shop"
    REFERRAL = "referral"
    HELP = "help"
    FREE_TEXT = "free_text"


@dataclass(slots=True, frozen=True, kw_only=True)
class UserMessageIntentResult:
    intent: UserMessageIntent
    confidence: float


__all__ = [
    "UserMessageIntent",
    "UserMessageIntentResult",
]
