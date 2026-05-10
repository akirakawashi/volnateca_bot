from dishka import Provider, Scope, provide

from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository
from application.interface.services import IUserMessageIntentClassifier
from application.services.award_task_service import AwardTaskService
from application.services.user_message_intent import RuleBasedUserMessageIntentClassifier


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

    @provide(scope=Scope.APP, provides=IUserMessageIntentClassifier)
    def get_user_message_intent_classifier(self) -> RuleBasedUserMessageIntentClassifier:
        return RuleBasedUserMessageIntentClassifier()
