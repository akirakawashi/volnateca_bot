import re

from application.common.dto.user_message import UserMessageIntent, UserMessageIntentResult
from application.interface.services import IUserMessageIntentClassifier


class RuleBasedUserMessageIntentClassifier(IUserMessageIntentClassifier):
    """
    Временный классификатор на правилах до подключения AI-ассистента.
    Асинхронная сигнатура оставлена без await, чтобы не ломать интерфейс,
    когда там будет AI-ассистент.
    """

    async def classify(self, *, text: str) -> UserMessageIntentResult:
        normalized_text = _normalize_text(text=text)
        if not normalized_text:
            return UserMessageIntentResult(intent=UserMessageIntent.HELP, confidence=1.0)

        if _has_any_token(normalized_text, BALANCE_TOKENS):
            return UserMessageIntentResult(intent=UserMessageIntent.BALANCE, confidence=1.0)
        if _has_any_token(normalized_text, TASKS_TOKENS):
            return UserMessageIntentResult(intent=UserMessageIntent.TASKS, confidence=1.0)
        if _has_any_token(normalized_text, SHOP_TOKENS):
            return UserMessageIntentResult(intent=UserMessageIntent.SHOP, confidence=1.0)
        if _has_any_token(normalized_text, REFERRAL_TOKENS):
            return UserMessageIntentResult(intent=UserMessageIntent.REFERRAL, confidence=1.0)
        if _has_any_token(normalized_text, HELP_TOKENS):
            return UserMessageIntentResult(intent=UserMessageIntent.HELP, confidence=1.0)

        return UserMessageIntentResult(intent=UserMessageIntent.FREE_TEXT, confidence=0.0)


BALANCE_TOKENS = frozenset(
    (
        "balance",
        "баланс",
        "баллы",
        "баллов",
        "дискошары",
        "очки",
        "счет",
        "счёт",
    ),
)
TASKS_TOKENS = frozenset(
    (
        "tasks",
        "task",
        "задание",
        "задания",
        "задачи",
        "квест",
        "квесты",
        "викторина",
        "викторины",
    ),
)
SHOP_TOKENS = frozenset(
    (
        "shop",
        "магазин",
        "приз",
        "призы",
        "подарок",
        "подарки",
        "промокод",
        "промокоды",
    ),
)
REFERRAL_TOKENS = frozenset(
    (
        "referral",
        "ref",
        "реферал",
        "рефералка",
        "рефералы",
        "друг",
        "друзья",
        "пригласить",
        "ссылка",
    ),
)
HELP_TOKENS = frozenset(
    (
        "help",
        "start",
        "помощь",
        "меню",
        "начать",
        "старт",
        "привет",
    ),
)
TOKEN_PATTERN = re.compile(r"[\wё]+", re.IGNORECASE)


def _normalize_text(*, text: str) -> str:
    return text.casefold().strip()


def _has_any_token(text: str, tokens: frozenset[str]) -> bool:
    return bool(tokens.intersection(TOKEN_PATTERN.findall(text)))


__all__ = ["RuleBasedUserMessageIntentClassifier"]
