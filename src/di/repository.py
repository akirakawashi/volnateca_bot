from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from application.interface.repositories.achievements import IAchievementRepository
from application.interface.repositories.quiz import IQuizRepository
from application.interface.repositories.referrals import IReferralRepository
from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.tasks import ITaskRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository
from infrastructure.database.repositories.achievements import AchievementRepository
from infrastructure.database.repositories.quiz import QuizRepository
from infrastructure.database.repositories.referrals import ReferralRepository
from infrastructure.database.repositories.task_completions import TaskCompletionRepository
from infrastructure.database.repositories.tasks import TaskRepository
from infrastructure.database.repositories.transactions import TransactionRepository
from infrastructure.database.repositories.users import UserRepository


class RepositoriesProvider(Provider):
    @provide(scope=Scope.REQUEST, provides=IUserRepository)
    def get_user_repository(
        self,
        session: AsyncSession,
    ) -> UserRepository:
        return UserRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=ITaskRepository)
    def get_task_repository(
        self,
        session: AsyncSession,
    ) -> TaskRepository:
        return TaskRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=ITaskCompletionRepository)
    def get_task_completion_repository(
        self,
        session: AsyncSession,
    ) -> TaskCompletionRepository:
        return TaskCompletionRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=ITransactionRepository)
    def get_transaction_repository(
        self,
        session: AsyncSession,
    ) -> TransactionRepository:
        return TransactionRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=IQuizRepository)
    def get_quiz_repository(
        self,
        session: AsyncSession,
    ) -> QuizRepository:
        return QuizRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=IReferralRepository)
    def get_referral_repository(
        self,
        session: AsyncSession,
    ) -> ReferralRepository:
        return ReferralRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=IAchievementRepository)
    def get_achievement_repository(
        self,
        session: AsyncSession,
    ) -> AchievementRepository:
        return AchievementRepository(session=session)
