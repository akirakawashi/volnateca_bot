from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from application.interface.repositories.achievements import IAchievementRepository
from application.interface.repositories.message_templates import IMessageTemplateRepository
from application.interface.repositories.prizes import IPrizeRepository
from application.interface.repositories.quiz import IQuizRepository
from application.admin.interface.db_manager import IDBManager
from application.admin.interface.repositories.prize import IPrizeAdminRepository
from application.admin.interface.repositories.quiz import IQuizAdminRepository
from application.admin.interface.repositories.task_promo_code import ITaskPromoCodeAdminRepository
from application.interface.repositories.referral_intents import IReferralIntentRepository
from application.interface.repositories.referrals import IReferralRepository
from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.task_promo_code_waits import ITaskPromoCodeWaitRepository
from application.interface.repositories.task_promo_codes import ITaskPromoCodeRepository
from application.interface.repositories.tasks import ITaskRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository
from infrastructure.database.repositories.achievements import AchievementRepository
from infrastructure.database.repositories.message_templates import MessageTemplateRepository
from infrastructure.database.repositories.prizes import PrizeRepository
from infrastructure.database.repositories.quiz import QuizRepository
from infrastructure.database.db_manager import DBManager
from infrastructure.database.repositories.admin.prize import PrizeAdminRepository
from infrastructure.database.repositories.admin.quiz import QuizAdminRepository
from infrastructure.database.repositories.admin.task_promo_code import TaskPromoCodeAdminRepository
from infrastructure.database.repositories.referral_intents import ReferralIntentRepository
from infrastructure.database.repositories.referrals import ReferralRepository
from infrastructure.database.repositories.task_completions import TaskCompletionRepository
from infrastructure.database.repositories.task_promo_code_waits import TaskPromoCodeWaitRepository
from infrastructure.database.repositories.task_promo_codes import TaskPromoCodeRepository
from infrastructure.database.repositories.tasks import TaskRepository
from infrastructure.database.repositories.transactions import TransactionRepository
from infrastructure.database.repositories.users import UserRepository


class RepositoriesProvider(Provider):
    @provide(scope=Scope.REQUEST, provides=IMessageTemplateRepository)
    def get_message_template_repository(
        self,
        session: AsyncSession,
    ) -> MessageTemplateRepository:
        return MessageTemplateRepository(session=session)

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

    @provide(scope=Scope.REQUEST, provides=ITaskPromoCodeRepository)
    def get_task_promo_code_repository(
        self,
        session: AsyncSession,
    ) -> TaskPromoCodeRepository:
        return TaskPromoCodeRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=ITaskPromoCodeWaitRepository)
    def get_task_promo_code_wait_repository(
        self,
        session: AsyncSession,
    ) -> TaskPromoCodeWaitRepository:
        return TaskPromoCodeWaitRepository(session=session)

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

    @provide(scope=Scope.REQUEST, provides=IPrizeRepository)
    def get_prize_repository(
        self,
        session: AsyncSession,
    ) -> PrizeRepository:
        return PrizeRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=IReferralRepository)
    def get_referral_repository(
        self,
        session: AsyncSession,
    ) -> ReferralRepository:
        return ReferralRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=IReferralIntentRepository)
    def get_referral_intent_repository(
        self,
        session: AsyncSession,
    ) -> ReferralIntentRepository:
        return ReferralIntentRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=IAchievementRepository)
    def get_achievement_repository(
        self,
        session: AsyncSession,
    ) -> AchievementRepository:
        return AchievementRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=IQuizAdminRepository)
    def get_quiz_admin_repository(
        self,
        session: AsyncSession,
    ) -> QuizAdminRepository:
        return QuizAdminRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=IPrizeAdminRepository)
    def get_prize_admin_repository(
        self,
        session: AsyncSession,
    ) -> PrizeAdminRepository:
        return PrizeAdminRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=ITaskPromoCodeAdminRepository)
    def get_task_promo_code_admin_repository(
        self,
        session: AsyncSession,
    ) -> TaskPromoCodeAdminRepository:
        return TaskPromoCodeAdminRepository(session=session)

    @provide(scope=Scope.REQUEST, provides=IDBManager)
    def get_db_manager(
        self,
        session: AsyncSession,
    ) -> DBManager:
        return DBManager(session=session)
