from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

# TODO: удалить SeedDevScenarioHandler и get_seed_dev_scenario_handler перед релизом.
from application.admin.command.seed_dev_scenario import SeedDevScenarioHandler
from application.command.answer_quiz_question import AnswerQuizQuestionHandler
from application.command.award_monthly_top import AwardMonthlyTopHandler
from application.command.complete_vk_comment_task import CompleteVKCommentTaskHandler
from application.command.complete_vk_like_task import CompleteVKLikeTaskHandler
from application.command.complete_vk_repost_task import CompleteVKRepostTaskHandler
from application.command.complete_vk_subscription_task import CompleteVKSubscriptionTaskHandler
from application.admin.command.create_quiz import CreateQuizHandler
from application.admin.command.post_to_wall import PostToWallHandler
from application.admin.command.truncate_db import TruncateDBHandler
from application.command.get_quiz_first_question import GetQuizFirstQuestionHandler
from application.command.get_vk_user_tasks import GetVKUserTasksHandler
from application.command.process_referral import ProcessReferralHandler
from application.command.record_vk_user_activity import RecordVKUserActivityHandler
from application.command.register_vk_user import RegisterVKUserHandler
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionHandler,
)
from application.interface.clients import IVKUserClient, IVKWallClient
from application.interface.repositories.achievements import IAchievementRepository
from application.interface.repositories.quiz import IQuizRepository
from application.admin.interface.db_manager import IDBManager
from application.admin.interface.repositories.quiz import IQuizAdminRepository
from application.interface.repositories.referrals import IReferralRepository
from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.tasks import ITaskRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.user_daily_activities import IUserDailyActivityRepository
from application.interface.repositories.users import IUserRepository
from application.interface.uow import IUnitOfWork
from application.services.award_achievement_service import AwardAchievementService
from application.services.award_task_service import AwardTaskService
from application.services.daily_streak_achievement_service import DailyStreakAchievementService
from application.services.quiz_streak_achievement_service import QuizStreakAchievementService
from settings.vk import VKSettings


class InteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_register_vk_user_handler(
        self,
        repository: IUserRepository,
        uow: IUnitOfWork,
        vk_user_client: IVKUserClient,
    ) -> RegisterVKUserHandler:
        return RegisterVKUserHandler(
            repository=repository,
            uow=uow,
            vk_user_client=vk_user_client,
        )

    @provide(scope=Scope.REQUEST)
    def get_register_vk_user_and_check_subscription_handler(
        self,
        register_vk_user_interactor: RegisterVKUserHandler,
        complete_vk_subscription_task_interactor: CompleteVKSubscriptionTaskHandler,
    ) -> RegisterVKUserAndCheckSubscriptionHandler:
        return RegisterVKUserAndCheckSubscriptionHandler(
            register_vk_user_interactor=register_vk_user_interactor,
            complete_vk_subscription_task_interactor=complete_vk_subscription_task_interactor,
        )

    @provide(scope=Scope.REQUEST)
    def get_complete_vk_repost_task_handler(
        self,
        task_repository: ITaskRepository,
        award_service: AwardTaskService,
        uow: IUnitOfWork,
    ) -> CompleteVKRepostTaskHandler:
        return CompleteVKRepostTaskHandler(
            task_repository=task_repository,
            award_service=award_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_complete_vk_subscription_task_handler(
        self,
        task_repository: ITaskRepository,
        task_completion_repository: ITaskCompletionRepository,
        award_service: AwardTaskService,
        uow: IUnitOfWork,
        vk_user_client: IVKUserClient,
        vk_settings: VKSettings,
    ) -> CompleteVKSubscriptionTaskHandler:
        return CompleteVKSubscriptionTaskHandler(
            task_repository=task_repository,
            task_completion_repository=task_completion_repository,
            award_service=award_service,
            uow=uow,
            vk_user_client=vk_user_client,
            required_subscription_group_id=vk_settings.required_subscription_group_id,
        )

    @provide(scope=Scope.REQUEST)
    def get_complete_vk_like_task_handler(
        self,
        task_repository: ITaskRepository,
        award_service: AwardTaskService,
        uow: IUnitOfWork,
    ) -> CompleteVKLikeTaskHandler:
        return CompleteVKLikeTaskHandler(
            task_repository=task_repository,
            award_service=award_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_complete_vk_comment_task_handler(
        self,
        task_repository: ITaskRepository,
        award_service: AwardTaskService,
        uow: IUnitOfWork,
    ) -> CompleteVKCommentTaskHandler:
        return CompleteVKCommentTaskHandler(
            task_repository=task_repository,
            award_service=award_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_vk_user_tasks_handler(
        self,
        task_repository: ITaskRepository,
    ) -> GetVKUserTasksHandler:
        return GetVKUserTasksHandler(task_repository=task_repository)

    @provide(scope=Scope.REQUEST)
    def get_quiz_first_question_handler(
        self,
        quiz_repository: IQuizRepository,
    ) -> GetQuizFirstQuestionHandler:
        return GetQuizFirstQuestionHandler(quiz_repository=quiz_repository)

    @provide(scope=Scope.REQUEST)
    def get_answer_quiz_question_handler(
        self,
        quiz_repository: IQuizRepository,
        task_repository: ITaskRepository,
        award_service: AwardTaskService,
        quiz_streak_achievement_service: QuizStreakAchievementService,
        uow: IUnitOfWork,
    ) -> AnswerQuizQuestionHandler:
        return AnswerQuizQuestionHandler(
            quiz_repository=quiz_repository,
            task_repository=task_repository,
            award_service=award_service,
            quiz_streak_achievement_service=quiz_streak_achievement_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_process_referral_handler(
        self,
        user_repository: IUserRepository,
        referral_repository: IReferralRepository,
        achievement_repository: IAchievementRepository,
        transaction_repository: ITransactionRepository,
        award_achievement_service: AwardAchievementService,
        uow: IUnitOfWork,
    ) -> ProcessReferralHandler:
        return ProcessReferralHandler(
            user_repository=user_repository,
            referral_repository=referral_repository,
            achievement_repository=achievement_repository,
            transaction_repository=transaction_repository,
            award_achievement_service=award_achievement_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_record_vk_user_activity_handler(
        self,
        user_repository: IUserRepository,
        daily_activity_repository: IUserDailyActivityRepository,
        daily_streak_achievement_service: DailyStreakAchievementService,
        uow: IUnitOfWork,
    ) -> RecordVKUserActivityHandler:
        return RecordVKUserActivityHandler(
            user_repository=user_repository,
            daily_activity_repository=daily_activity_repository,
            daily_streak_achievement_service=daily_streak_achievement_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_award_monthly_top_handler(
        self,
        transaction_repository: ITransactionRepository,
        achievement_repository: IAchievementRepository,
        award_achievement_service: AwardAchievementService,
        uow: IUnitOfWork,
    ) -> AwardMonthlyTopHandler:
        return AwardMonthlyTopHandler(
            transaction_repository=transaction_repository,
            achievement_repository=achievement_repository,
            award_achievement_service=award_achievement_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_create_quiz_handler(
        self,
        quiz_admin_repository: IQuizAdminRepository,
        uow: IUnitOfWork,
    ) -> CreateQuizHandler:
        return CreateQuizHandler(
            quiz_admin_repository=quiz_admin_repository,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_post_to_wall_handler(
        self,
        vk_wall_client: IVKWallClient,
        task_repository: ITaskRepository,
        uow: IUnitOfWork,
        vk_settings: VKSettings,
    ) -> PostToWallHandler:
        return PostToWallHandler(
            vk_wall_client=vk_wall_client,
            task_repository=task_repository,
            uow=uow,
            vk_settings=vk_settings,
        )

    @provide(scope=Scope.REQUEST)
    def get_truncate_db_handler(
        self,
        db_manager: IDBManager,
    ) -> TruncateDBHandler:
        return TruncateDBHandler(db_manager=db_manager)

    @provide(scope=Scope.REQUEST)
    def get_seed_dev_scenario_handler(
        self,
        session: AsyncSession,
        vk_settings: VKSettings,
    ) -> "SeedDevScenarioHandler":
        from application.admin.command.seed_dev_scenario import SeedDevScenarioHandler
        return SeedDevScenarioHandler(session=session, vk_settings=vk_settings)
