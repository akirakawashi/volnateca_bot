from application.base_interactor import Interactor
from application.admin.dto.prize import CreatePrizeCommand, PrizeAdminDTO
from application.admin.interface.repositories.prize import IPrizeAdminRepository
from application.interface.uow import IUnitOfWork


class CreatePrizeHandler(Interactor[CreatePrizeCommand, PrizeAdminDTO]):
    def __init__(
        self,
        prize_admin_repository: IPrizeAdminRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.prize_admin_repository = prize_admin_repository
        self.uow = uow

    async def __call__(self, command_data: CreatePrizeCommand) -> PrizeAdminDTO:
        result = await self.prize_admin_repository.create_prize(command_data)
        await self.uow.commit()
        return result


__all__ = ["CreatePrizeHandler"]
