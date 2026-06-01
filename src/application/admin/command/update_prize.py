from application.admin.command.prize import UpdatePrizeCommand
from application.admin.dto.prize import PrizeAdminDTO
from application.admin.interface.repositories.prize import IPrizeAdminRepository
from application.base_interactor import Interactor
from application.interface.uow import IUnitOfWork


class UpdatePrizeHandler(Interactor[UpdatePrizeCommand, PrizeAdminDTO | None]):
    def __init__(
        self,
        prize_admin_repository: IPrizeAdminRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.prize_admin_repository = prize_admin_repository
        self.uow = uow

    async def __call__(self, command_data: UpdatePrizeCommand) -> PrizeAdminDTO | None:
        result = await self.prize_admin_repository.update_prize(command_data)
        if result is None:
            return None
        await self.uow.commit()
        return result


__all__ = ["UpdatePrizeHandler"]
