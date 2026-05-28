from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.admin.interface.broadcast_recipients import IBroadcastRecipientReader
from application.admin.services import BroadcastManager
from application.interface.clients import IVKMessageClient
from application.interface.repositories.achievements import IAchievementRepository
from application.interface.repositories.message_templates import IMessageTemplateRepository
from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.tasks import ITaskRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository
from application.interface.services import IVKMessageTemplateService
from application.services.award_achievement_service import AwardAchievementService
from application.services.award_task_service import AwardTaskService
from application.services.project_completion_achievement_service import ProjectCompletionAchievementService
from application.services.vk_message_template_service import VKMessageTemplateService
from application.services.week_completion_achievement_service import WeekCompletionAchievementService
from infrastructure.database.repositories.broadcast_recipients import SQLAlchemyBroadcastRecipientReader


class ServicesProvider(Provider):
    @provide(scope=Scope.APP, provides=IBroadcastRecipientReader)
    def get_broadcast_recipient_reader(
        self,
        pool: async_sessionmaker[AsyncSession],
    ) -> SQLAlchemyBroadcastRecipientReader:
        return SQLAlchemyBroadcastRecipientReader(session_pool=pool)

    @provide(scope=Scope.APP)
    def get_broadcast_manager(
        self,
        recipient_reader: IBroadcastRecipientReader,
        message_client: IVKMessageClient,
    ) -> BroadcastManager:
        return BroadcastManager(
            recipient_reader=recipient_reader,
            message_client=message_client,
        )

    @provide(scope=Scope.REQUEST, provides=IVKMessageTemplateService)
    def get_vk_message_template_service(
        self,
        message_templates: IMessageTemplateRepository,
    ) -> VKMessageTemplateService:
        return VKMessageTemplateService(repository=message_templates)

    @provide(scope=Scope.REQUEST)
    def get_award_achievement_service(
        self,
        users: IUserRepository,
        achievements: IAchievementRepository,
        transactions: ITransactionRepository,
    ) -> AwardAchievementService:
        return AwardAchievementService(
            users=users,
            achievements=achievements,
            transactions=transactions,
        )

    @provide(scope=Scope.REQUEST)
    def get_award_task_service(
        self,
        users: IUserRepository,
        task_completions: ITaskCompletionRepository,
        transactions: ITransactionRepository,
        week_completion_achievements: WeekCompletionAchievementService,
        project_completion_achievements: ProjectCompletionAchievementService,
    ) -> AwardTaskService:
        return AwardTaskService(
            users=users,
            task_completions=task_completions,
            transactions=transactions,
            week_completion_achievements=week_completion_achievements,
            project_completion_achievements=project_completion_achievements,
        )

    @provide(scope=Scope.REQUEST)
    def get_week_completion_achievement_service(
        self,
        tasks: ITaskRepository,
        achievements: IAchievementRepository,
        award_achievement_service: AwardAchievementService,
    ) -> WeekCompletionAchievementService:
        return WeekCompletionAchievementService(
            tasks=tasks,
            achievements=achievements,
            award_achievement_service=award_achievement_service,
        )

    @provide(scope=Scope.REQUEST)
    def get_project_completion_achievement_service(
        self,
        achievements: IAchievementRepository,
        award_achievement_service: AwardAchievementService,
    ) -> ProjectCompletionAchievementService:
        return ProjectCompletionAchievementService(
            achievements=achievements,
            award_achievement_service=award_achievement_service,
        )
