from dishka import Provider, Scope, provide

from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository
from application.services.award_task_service import AwardTaskService


class ServicesProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_award_task_service(
        self,
        users: IUserRepository,
        task_completions: ITaskCompletionRepository,
        transactions: ITransactionRepository,
    ) -> AwardTaskService:
        return AwardTaskService(
            users=users,
            task_completions=task_completions,
            transactions=transactions,
        )
