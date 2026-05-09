from abc import ABC, abstractmethod

from application.common.dto.user import VKUserRegistrationDTO
from application.common.dto.wallet import UserBalanceSnapshot


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_vk_user_id(
        self,
        vk_user_id: int,
    ) -> VKUserRegistrationDTO | None:
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
    async def update_profile(
        self,
        users_id: int,
        first_name: str | None,
        last_name: str | None,
        vk_screen_name: str | None,
    ) -> VKUserRegistrationDTO:
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
    ) -> None:
        """Записывает в таблицу users новые значения баланса и накопленных
        очков, рассчитанные WalletService.
        """

        raise NotImplementedError
