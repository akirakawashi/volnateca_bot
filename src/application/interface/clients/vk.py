from abc import ABC, abstractmethod

from application.common.dto.vk import VKUserProfileDTO


class IVKUserClient(ABC):
    """Порт чтения пользовательских данных и членства во VK-группе."""

    @abstractmethod
    async def get_user_profile(self, vk_user_id: int) -> VKUserProfileDTO | None:
        """Возвращает профиль VK или None, если API недоступен/не дал данные."""

        raise NotImplementedError

    @abstractmethod
    async def is_group_member(self, vk_user_id: int, group_id: int) -> bool | None:
        """Возвращает membership-флаг или None, если VK API не дал надёжный ответ."""

        raise NotImplementedError


class IVKMessageClient(ABC):
    """Порт отправки сообщений пользователям VK."""

    @abstractmethod
    async def send_message(
        self,
        *,
        vk_user_id: int,
        message: str,
        random_id: int | None = None,
        keyboard: dict[str, object] | None = None,
    ) -> bool:
        """Возвращает True только когда VK подтвердил отправку сообщения."""

        raise NotImplementedError
