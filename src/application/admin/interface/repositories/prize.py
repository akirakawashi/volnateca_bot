from abc import ABC, abstractmethod

from application.admin.command.prize import CreatePrizeCommand, UpdatePrizeCommand
from application.admin.dto.prize import PrizeAdminDTO


class IPrizeAdminRepository(ABC):
    @abstractmethod
    async def list_prizes(self) -> tuple[PrizeAdminDTO, ...]:
        raise NotImplementedError

    @abstractmethod
    async def create_prize(self, command: CreatePrizeCommand) -> PrizeAdminDTO:
        raise NotImplementedError

    @abstractmethod
    async def update_prize(self, command: UpdatePrizeCommand) -> PrizeAdminDTO | None:
        raise NotImplementedError


__all__ = ["IPrizeAdminRepository"]
