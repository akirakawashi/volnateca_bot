from abc import ABC, abstractmethod


class IReferralRepository(ABC):
    @abstractmethod
    async def create_if_not_exists(
        self,
        inviter_users_id: int,
        invited_users_id: int,
    ) -> tuple[int, bool]:
        """Создаёт реферальную связь. Возвращает (referrals_id, created).

        Если приглашённый пользователь уже имеет реферера — возвращает
        существующую запись с created=False.
        """
        raise NotImplementedError

    @abstractmethod
    async def count_referrals(self, inviter_users_id: int) -> int:
        """Возвращает количество пользователей, приглашённых данным инвайтером."""
        raise NotImplementedError

    @abstractmethod
    async def set_bonus_transaction(
        self,
        referrals_id: int,
        transactions_id: int,
    ) -> None:
        """Проставляет ID транзакции реферального бонуса на запись реферала."""
        raise NotImplementedError


__all__ = ["IReferralRepository"]
