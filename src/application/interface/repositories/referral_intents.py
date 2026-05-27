from abc import ABC, abstractmethod


class IReferralIntentRepository(ABC):
    @abstractmethod
    async def create_if_absent(
        self,
        *,
        invited_vk_user_id: int,
        raw_ref: str,
    ) -> None:
        """Сохраняет первый ref пользователя до регистрации, не перезаписывая его."""

        raise NotImplementedError

    @abstractmethod
    async def get_raw_ref(
        self,
        *,
        invited_vk_user_id: int,
    ) -> str | None:
        raise NotImplementedError
