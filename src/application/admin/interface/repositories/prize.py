from abc import ABC, abstractmethod

from application.admin.dto.prize import CreatePrizeCommand, PrizeAdminDTO


class IPrizeAdminRepository(ABC):
    @abstractmethod
    async def list_prizes(self) -> tuple[PrizeAdminDTO, ...]:
        raise NotImplementedError

    @abstractmethod
    async def create_prize(self, command: CreatePrizeCommand) -> PrizeAdminDTO:
        raise NotImplementedError


__all__ = ["IPrizeAdminRepository"]
