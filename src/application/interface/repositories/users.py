from abc import ABC, abstractmethod

from application.common.dto.user import ActiveVKUserDTO, VKUserRegistrationDTO
from application.common.dto.wallet import UserBalanceSnapshot


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_vk_user_id(
        self,
        vk_user_id: int,
    ) -> VKUserRegistrationDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def count_active_users(self) -> int:
        """Возвращает количество активных зарегистрированных пользователей."""

        raise NotImplementedError

    @abstractmethod
    async def list_active_users_page(
        self,
        *,
        after_users_id: int | None,
        limit: int,
    ) -> tuple[ActiveVKUserDTO, ...]:
        """Возвращает страницу активных пользователей через keyset pagination."""

        raise NotImplementedError

    @abstractmethod
    async def create_registered_user(
        self,
        vk_user_id: int,
        first_name: str | None,
        last_name: str | None,
        vk_screen_name: str | None,
        bonus_points: int,
    ) -> VKUserRegistrationDTO:
        raise NotImplementedError

    @abstractmethod
    async def update_vk_profile(
        self,
        *,
        vk_user_id: int,
        first_name: str | None,
        last_name: str | None,
        vk_screen_name: str | None,
    ) -> None:
        """Обновляет профильные поля пользователя без изменения баланса."""

        raise NotImplementedError

    @abstractmethod
    async def get_balance_snapshot_by_users_id_for_update(
        self,
        users_id: int,
    ) -> UserBalanceSnapshot | None:
        """Блокирует пользователя по users_id и возвращает снимок баланса."""

        raise NotImplementedError

    @abstractmethod
    async def get_balance_snapshot_for_update(
        self,
        vk_user_id: int,
    ) -> UserBalanceSnapshot | None:
        """Возвращает снимок баланса пользователя с блокировкой строки.

        Должен выполняться в открытой транзакции; блокировка снимается на
        commit/rollback. Используется AwardTaskService для атомарного
        изменения баланса.
        """

        raise NotImplementedError

    @abstractmethod
    async def apply_balance_change(
        self,
        *,
        users_id: int,
        balance_points: int,
        earned_points_total: int,
        current_level: int,
    ) -> None:
        """Записывает в таблицу users новые значения баланса и накопленных
        очков, рассчитанные WalletService.
        """

        raise NotImplementedError

    @abstractmethod
    async def apply_spend(
        self,
        *,
        users_id: int,
        balance_points: int,
        spent_points_total: int,
    ) -> None:
        """Записывает баланс и spent_points_total после списания за приз."""

        raise NotImplementedError

    @abstractmethod
    async def apply_refund(
        self,
        *,
        users_id: int,
        balance_points: int,
        spent_points_total: int,
    ) -> None:
        """Записывает баланс и spent_points_total после возврата за отменённый приз."""

        raise NotImplementedError
