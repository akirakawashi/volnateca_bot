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
        attachment: str | None = None,
    ) -> bool:
        """Возвращает True только когда VK подтвердил отправку сообщения."""

        raise NotImplementedError

    @abstractmethod
    async def upload_photo_for_message(self, image_url: str) -> str | None:
        """Загружает изображение по URL на серверы VK и возвращает строку вложения.

        Возвращает строку формата ``photo{owner_id}_{media_id}`` при успехе
        или None при любой ошибке.
        """

        raise NotImplementedError


class IVKWallClient(ABC):
    """Порт публикации записей на стене сообщества."""

    @abstractmethod
    async def post_to_wall(
        self,
        *,
        message: str,
        attachments: tuple[str, ...] | None = None,
    ) -> int | None:
        """Публикует запись от имени сообщества.

        Возвращает post_id при успехе или None при ошибке.
        """

        raise NotImplementedError
