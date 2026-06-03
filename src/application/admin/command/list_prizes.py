from application.base_interactor import Interactor
from application.admin.command.prize import ListPrizesCommand
from application.admin.dto.prize import PrizeAdminDTO
from application.admin.interface.repositories.prize import IPrizeAdminRepository


class ListPrizesHandler(Interactor[ListPrizesCommand, tuple[PrizeAdminDTO, ...]]):
    def __init__(self, prize_admin_repository: IPrizeAdminRepository) -> None:
        self.prize_admin_repository = prize_admin_repository

    async def __call__(self, command_data: ListPrizesCommand) -> tuple[PrizeAdminDTO, ...]:
        del command_data
        return await self.prize_admin_repository.list_prizes()


__all__ = ["ListPrizesHandler"]
