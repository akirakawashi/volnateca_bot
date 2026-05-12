from application.base_interactor import Interactor
from application.admin.dto.quiz import CreateQuizCommand, CreatedQuizDTO
from application.admin.interface.repositories.quiz import IQuizAdminRepository
from application.interface.uow import IUnitOfWork


class CreateQuizHandler(Interactor[CreateQuizCommand, CreatedQuizDTO]):
    """Создаёт квиз (задание + вопросы + варианты) и сохраняет в БД."""

    def __init__(
        self,
        quiz_admin_repository: IQuizAdminRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.quiz_admin_repository = quiz_admin_repository
        self.uow = uow

    async def __call__(self, command_data: CreateQuizCommand) -> CreatedQuizDTO:
        result = await self.quiz_admin_repository.create_quiz(command_data)
        await self.uow.commit()
        return result
