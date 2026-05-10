from abc import ABC, abstractmethod

from application.common.dto.user_message import UserMessageIntentResult


class IUserMessageIntentClassifier(ABC):
    """Точка расширения для будущего AI-ассистента, классифицирующего сообщения."""

    @abstractmethod
    async def classify(self, *, text: str) -> UserMessageIntentResult:
        raise NotImplementedError
