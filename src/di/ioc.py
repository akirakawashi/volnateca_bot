from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from application.admin.command.broadcast import GetBroadcastStatusHandler, StartBroadcastHandler

# TODO DEV: удалить импорты SeedDevScenarioHandler, TruncateDBHandler перед релизом.
from application.admin.command.seed_dev_scenario import SeedDevScenarioHandler
from application.admin.command.create_prize import CreatePrizeHandler
from application.admin.command.prize_promo_code import AddPrizePromoCodesHandler
from application.admin.command.update_prize import UpdatePrizeHandler
from application.admin.command.prize_redemption import (
    CancelPrizeRedemptionHandler,
    FulfillPrizeRedemptionHandler,
    GetPrizeRedemptionByCodeHandler,
    GetPrizeRedemptionHandler,
    GetPrizeRedemptionQueueCountHandler,
    ListPrizeRedemptionsHandler,
)
from application.admin.command.user import (
    GetUserProfileHandler,
    GetUserReferralsHandler,
    ListUserPrizeRedemptionsHandler,
    ListUserTaskCompletionsHandler,
    ListUserTransactionsHandler,
    SearchUsersHandler,
    UserExistsHandler,
)
from application.admin.interface.repositories.stats import IStatsAdminRepository
from application.admin.interface.repositories.user import IUserAdminRepository
from application.admin.command.list_prizes import ListPrizesHandler
from application.admin.command.stats import (
    GetAccrualSourcesStatsHandler,
    GetDailyAccrualPointsStatsHandler,
    GetDailyActivityStatsHandler,
    GetDailyNewUsersStatsHandler,
)
from application.admin.command.message_templates import (
    DeleteMessageTemplateHandler,
    ListMessageTemplatesHandler,
    UpsertMessageTemplateHandler,
)
from application.command.answer_quiz_question import AnswerQuizQuestionHandler
from application.command.award_monthly_top import AwardMonthlyTopHandler
from application.command.capture_vk_referral_intent import CaptureVKReferralIntentHandler
from application.command.complete_vk_comment_task import CompleteVKCommentTaskHandler
from application.command.complete_vk_like_task import CompleteVKLikeTaskHandler
from application.command.complete_vk_poll_task import CompleteVKPollTaskHandler
from application.command.complete_vk_subscription_task import CompleteVKSubscriptionTaskHandler
from application.admin.command.create_quiz import CreateQuizHandler
from application.admin.command.quiz import ListQuizzesHandler, UpdateQuizQuestionImageHandler
from application.admin.command.post_to_wall import PostToWallHandler
from application.admin.command.truncate_db import TruncateDBHandler  # TODO DEV: удалить перед релизом.
from application.admin.command.task_promo_code import (
    CreateTaskPromoCodeTaskHandler,
    ListTaskPromoCodeTasksHandler,
    UpdateTaskPromoCodeTaskHandler,
)
from application.command.ensure_vk_poll_task import EnsureVKPollTaskHandler
from application.command.get_quiz_first_question import GetQuizFirstQuestionHandler
from application.command.get_store_catalog import GetStoreCatalogHandler, GetStorePrizeCardHandler
from application.command.list_user_redemptions import ListUserRedemptionsHandler
from application.command.redeem_prize import RedeemPrizeHandler
from application.command.get_vk_user_tasks import GetVKUserTasksHandler
from application.command.process_referral import ProcessReferralHandler
from application.command.register_vk_user import RegisterVKUserHandler
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionHandler,
)
from application.command.register_vk_user_with_referral_context import (
    RegisterVKUserWithReferralContextHandler,
)
from application.command.task_promo_code import (
    ActivateTaskPromoCodeHandler,
    CancelTaskPromoCodeHandler,
    GetTaskPromoCodeWaitHandler,
    StartTaskPromoCodeHandler,
)
from application.interface.clients import IVKUserClient, IVKWallClient
from application.interface.services import IVKMessageTemplateService
from application.interface.repositories.achievements import IAchievementRepository
from application.interface.repositories.prize_promo_codes import IPrizePromoCodeRepository
from application.interface.repositories.prize_redemptions import IPrizeRedemptionRepository
from application.interface.repositories.prizes import IPrizeRepository
from application.interface.repositories.quiz import IQuizRepository
from application.admin.interface.db_manager import IDBManager  # TODO DEV: удалить перед релизом.
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
from application.interface.uow import IUnitOfWork
from application.admin.services import BroadcastManager
from application.services.award_achievement_service import AwardAchievementService
from application.services.award_task_service import AwardTaskService
from application.services.cancel_redemption_service import CancelRedemptionService
from application.services.fulfill_redemption_service import FulfillRedemptionService
from application.services.redeem_prize_service import RedeemPrizeService
from settings.app.app import AppSettings
from settings.vk import VKSettings


class InteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_start_broadcast_handler(
        self,
        broadcast_manager: BroadcastManager,
    ) -> StartBroadcastHandler:
        return StartBroadcastHandler(broadcast_manager=broadcast_manager)

    @provide(scope=Scope.REQUEST)
    def get_broadcast_status_handler(
        self,
        broadcast_manager: BroadcastManager,
    ) -> GetBroadcastStatusHandler:
        return GetBroadcastStatusHandler(broadcast_manager=broadcast_manager)

    @provide(scope=Scope.REQUEST)
    def get_list_message_templates_handler(
        self,
        service: IVKMessageTemplateService,
    ) -> ListMessageTemplatesHandler:
        return ListMessageTemplatesHandler(service=service)

    @provide(scope=Scope.REQUEST)
    def get_upsert_message_template_handler(
        self,
        service: IVKMessageTemplateService,
        uow: IUnitOfWork,
    ) -> UpsertMessageTemplateHandler:
        return UpsertMessageTemplateHandler(service=service, uow=uow)

    @provide(scope=Scope.REQUEST)
    def get_delete_message_template_handler(
        self,
        service: IVKMessageTemplateService,
        uow: IUnitOfWork,
    ) -> DeleteMessageTemplateHandler:
        return DeleteMessageTemplateHandler(service=service, uow=uow)

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
    def get_capture_vk_referral_intent_handler(
        self,
        referral_intent_repository: IReferralIntentRepository,
        uow: IUnitOfWork,
    ) -> CaptureVKReferralIntentHandler:
        return CaptureVKReferralIntentHandler(
            referral_intent_repository=referral_intent_repository,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_register_vk_user_with_referral_context_handler(
        self,
        register_vk_user_interactor: RegisterVKUserAndCheckSubscriptionHandler,
        process_referral_interactor: ProcessReferralHandler,
        referral_intent_repository: IReferralIntentRepository,
    ) -> RegisterVKUserWithReferralContextHandler:
        return RegisterVKUserWithReferralContextHandler(
            register_vk_user_interactor=register_vk_user_interactor,
            process_referral_interactor=process_referral_interactor,
            referral_intent_repository=referral_intent_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_complete_vk_subscription_task_handler(
        self,
        user_repository: IUserRepository,
        task_repository: ITaskRepository,
        task_completion_repository: ITaskCompletionRepository,
        award_service: AwardTaskService,
        uow: IUnitOfWork,
        vk_user_client: IVKUserClient,
        vk_settings: VKSettings,
    ) -> CompleteVKSubscriptionTaskHandler:
        return CompleteVKSubscriptionTaskHandler(
            user_repository=user_repository,
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
    def get_complete_vk_poll_task_handler(
        self,
        task_repository: ITaskRepository,
        award_service: AwardTaskService,
        uow: IUnitOfWork,
    ) -> CompleteVKPollTaskHandler:
        return CompleteVKPollTaskHandler(
            task_repository=task_repository,
            award_service=award_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_ensure_vk_poll_task_handler(
        self,
        task_repository: ITaskRepository,
        uow: IUnitOfWork,
    ) -> EnsureVKPollTaskHandler:
        return EnsureVKPollTaskHandler(
            task_repository=task_repository,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_vk_user_tasks_handler(
        self,
        task_repository: ITaskRepository,
    ) -> GetVKUserTasksHandler:
        return GetVKUserTasksHandler(task_repository=task_repository)

    @provide(scope=Scope.REQUEST)
    def get_store_catalog_handler(
        self,
        prize_repository: IPrizeRepository,
    ) -> GetStoreCatalogHandler:
        return GetStoreCatalogHandler(prize_repository=prize_repository)

    @provide(scope=Scope.REQUEST)
    def get_store_prize_card_handler(
        self,
        prize_repository: IPrizeRepository,
    ) -> GetStorePrizeCardHandler:
        return GetStorePrizeCardHandler(prize_repository=prize_repository)

    @provide(scope=Scope.REQUEST)
    def get_redeem_prize_handler(
        self,
        redeem_prize_service: RedeemPrizeService,
        uow: IUnitOfWork,
    ) -> RedeemPrizeHandler:
        return RedeemPrizeHandler(
            redeem_prize_service=redeem_prize_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_list_user_redemptions_handler(
        self,
        prize_redemption_repository: IPrizeRedemptionRepository,
    ) -> ListUserRedemptionsHandler:
        return ListUserRedemptionsHandler(
            prize_redemption_repository=prize_redemption_repository,
        )

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
        uow: IUnitOfWork,
    ) -> AnswerQuizQuestionHandler:
        return AnswerQuizQuestionHandler(
            quiz_repository=quiz_repository,
            task_repository=task_repository,
            award_service=award_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_start_task_promo_code_handler(
        self,
        user_repository: IUserRepository,
        task_repository: ITaskRepository,
        wait_repository: ITaskPromoCodeWaitRepository,
        uow: IUnitOfWork,
    ) -> StartTaskPromoCodeHandler:
        return StartTaskPromoCodeHandler(
            user_repository=user_repository,
            task_repository=task_repository,
            wait_repository=wait_repository,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_activate_task_promo_code_handler(
        self,
        user_repository: IUserRepository,
        task_repository: ITaskRepository,
        task_completion_repository: ITaskCompletionRepository,
        promo_code_repository: ITaskPromoCodeRepository,
        wait_repository: ITaskPromoCodeWaitRepository,
        award_service: AwardTaskService,
        uow: IUnitOfWork,
    ) -> ActivateTaskPromoCodeHandler:
        return ActivateTaskPromoCodeHandler(
            user_repository=user_repository,
            task_repository=task_repository,
            task_completion_repository=task_completion_repository,
            promo_code_repository=promo_code_repository,
            wait_repository=wait_repository,
            award_service=award_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_cancel_task_promo_code_handler(
        self,
        user_repository: IUserRepository,
        wait_repository: ITaskPromoCodeWaitRepository,
        uow: IUnitOfWork,
    ) -> CancelTaskPromoCodeHandler:
        return CancelTaskPromoCodeHandler(
            user_repository=user_repository,
            wait_repository=wait_repository,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_task_promo_code_wait_handler(
        self,
        user_repository: IUserRepository,
        wait_repository: ITaskPromoCodeWaitRepository,
    ) -> GetTaskPromoCodeWaitHandler:
        return GetTaskPromoCodeWaitHandler(
            user_repository=user_repository,
            wait_repository=wait_repository,
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
    def get_award_monthly_top_handler(
        self,
        transaction_repository: ITransactionRepository,
        achievement_repository: IAchievementRepository,
        award_achievement_service: AwardAchievementService,
        uow: IUnitOfWork,
        app_settings: AppSettings,
    ) -> AwardMonthlyTopHandler:
        return AwardMonthlyTopHandler(
            transaction_repository=transaction_repository,
            achievement_repository=achievement_repository,
            award_achievement_service=award_achievement_service,
            uow=uow,
            project_timezone=app_settings.project_timezone,
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
    def get_list_quizzes_handler(
        self,
        quiz_admin_repository: IQuizAdminRepository,
    ) -> ListQuizzesHandler:
        return ListQuizzesHandler(quiz_admin_repository=quiz_admin_repository)

    @provide(scope=Scope.REQUEST)
    def get_update_quiz_question_image_handler(
        self,
        quiz_admin_repository: IQuizAdminRepository,
        uow: IUnitOfWork,
    ) -> UpdateQuizQuestionImageHandler:
        return UpdateQuizQuestionImageHandler(
            quiz_admin_repository=quiz_admin_repository,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_list_prizes_handler(
        self,
        prize_admin_repository: IPrizeAdminRepository,
    ) -> ListPrizesHandler:
        return ListPrizesHandler(prize_admin_repository=prize_admin_repository)

    @provide(scope=Scope.REQUEST)
    def get_create_prize_handler(
        self,
        prize_admin_repository: IPrizeAdminRepository,
        uow: IUnitOfWork,
    ) -> CreatePrizeHandler:
        return CreatePrizeHandler(
            prize_admin_repository=prize_admin_repository,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_update_prize_handler(
        self,
        prize_admin_repository: IPrizeAdminRepository,
        uow: IUnitOfWork,
    ) -> UpdatePrizeHandler:
        return UpdatePrizeHandler(
            prize_admin_repository=prize_admin_repository,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_add_prize_promo_codes_handler(
        self,
        prize_promo_code_repository: IPrizePromoCodeRepository,
        uow: IUnitOfWork,
    ) -> AddPrizePromoCodesHandler:
        return AddPrizePromoCodesHandler(
            prize_promo_code_repository=prize_promo_code_repository,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_list_prize_redemptions_handler(
        self,
        prize_redemption_repository: IPrizeRedemptionRepository,
    ) -> ListPrizeRedemptionsHandler:
        return ListPrizeRedemptionsHandler(
            prize_redemption_repository=prize_redemption_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_get_prize_redemption_handler(
        self,
        prize_redemption_repository: IPrizeRedemptionRepository,
    ) -> GetPrizeRedemptionHandler:
        return GetPrizeRedemptionHandler(
            prize_redemption_repository=prize_redemption_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_get_prize_redemption_by_code_handler(
        self,
        prize_redemption_repository: IPrizeRedemptionRepository,
    ) -> GetPrizeRedemptionByCodeHandler:
        return GetPrizeRedemptionByCodeHandler(
            prize_redemption_repository=prize_redemption_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_get_prize_redemption_queue_count_handler(
        self,
        prize_redemption_repository: IPrizeRedemptionRepository,
    ) -> GetPrizeRedemptionQueueCountHandler:
        return GetPrizeRedemptionQueueCountHandler(
            prize_redemption_repository=prize_redemption_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_fulfill_prize_redemption_handler(
        self,
        fulfill_redemption_service: FulfillRedemptionService,
        uow: IUnitOfWork,
    ) -> FulfillPrizeRedemptionHandler:
        return FulfillPrizeRedemptionHandler(
            fulfill_redemption_service=fulfill_redemption_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_cancel_prize_redemption_handler(
        self,
        cancel_redemption_service: CancelRedemptionService,
        uow: IUnitOfWork,
    ) -> CancelPrizeRedemptionHandler:
        return CancelPrizeRedemptionHandler(
            cancel_redemption_service=cancel_redemption_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_daily_activity_stats_handler(
        self,
        stats_admin_repository: IStatsAdminRepository,
        app_settings: AppSettings,
    ) -> GetDailyActivityStatsHandler:
        return GetDailyActivityStatsHandler(
            stats_repository=stats_admin_repository,
            project_timezone=app_settings.project_timezone,
        )

    @provide(scope=Scope.REQUEST)
    def get_daily_new_users_stats_handler(
        self,
        stats_admin_repository: IStatsAdminRepository,
        app_settings: AppSettings,
    ) -> GetDailyNewUsersStatsHandler:
        return GetDailyNewUsersStatsHandler(
            stats_repository=stats_admin_repository,
            project_timezone=app_settings.project_timezone,
        )

    @provide(scope=Scope.REQUEST)
    def get_daily_accrual_points_stats_handler(
        self,
        stats_admin_repository: IStatsAdminRepository,
        app_settings: AppSettings,
    ) -> GetDailyAccrualPointsStatsHandler:
        return GetDailyAccrualPointsStatsHandler(
            stats_repository=stats_admin_repository,
            project_timezone=app_settings.project_timezone,
        )

    @provide(scope=Scope.REQUEST)
    def get_accrual_sources_stats_handler(
        self,
        stats_admin_repository: IStatsAdminRepository,
        app_settings: AppSettings,
    ) -> GetAccrualSourcesStatsHandler:
        return GetAccrualSourcesStatsHandler(
            stats_repository=stats_admin_repository,
            project_timezone=app_settings.project_timezone,
        )

    @provide(scope=Scope.REQUEST)
    def get_search_users_handler(
        self,
        user_admin_repository: IUserAdminRepository,
    ) -> SearchUsersHandler:
        return SearchUsersHandler(user_admin_repository=user_admin_repository)

    @provide(scope=Scope.REQUEST)
    def get_get_user_profile_handler(
        self,
        user_admin_repository: IUserAdminRepository,
    ) -> GetUserProfileHandler:
        return GetUserProfileHandler(user_admin_repository=user_admin_repository)

    @provide(scope=Scope.REQUEST)
    def get_user_exists_handler(
        self,
        user_admin_repository: IUserAdminRepository,
    ) -> UserExistsHandler:
        return UserExistsHandler(user_admin_repository=user_admin_repository)

    @provide(scope=Scope.REQUEST)
    def get_list_user_prize_redemptions_handler(
        self,
        prize_redemption_repository: IPrizeRedemptionRepository,
    ) -> ListUserPrizeRedemptionsHandler:
        return ListUserPrizeRedemptionsHandler(
            prize_redemption_repository=prize_redemption_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_list_user_task_completions_handler(
        self,
        task_completion_repository: ITaskCompletionRepository,
    ) -> ListUserTaskCompletionsHandler:
        return ListUserTaskCompletionsHandler(
            task_completion_repository=task_completion_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_list_user_transactions_handler(
        self,
        transaction_repository: ITransactionRepository,
    ) -> ListUserTransactionsHandler:
        return ListUserTransactionsHandler(
            transaction_repository=transaction_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_get_user_referrals_handler(
        self,
        user_admin_repository: IUserAdminRepository,
    ) -> GetUserReferralsHandler:
        return GetUserReferralsHandler(user_admin_repository=user_admin_repository)

    @provide(scope=Scope.REQUEST)
    def get_create_task_promo_code_task_handler(
        self,
        task_promo_code_admin_repository: ITaskPromoCodeAdminRepository,
        uow: IUnitOfWork,
    ) -> CreateTaskPromoCodeTaskHandler:
        return CreateTaskPromoCodeTaskHandler(
            repository=task_promo_code_admin_repository,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_list_task_promo_code_tasks_handler(
        self,
        task_promo_code_admin_repository: ITaskPromoCodeAdminRepository,
    ) -> ListTaskPromoCodeTasksHandler:
        return ListTaskPromoCodeTasksHandler(repository=task_promo_code_admin_repository)

    @provide(scope=Scope.REQUEST)
    def get_update_task_promo_code_task_handler(
        self,
        task_promo_code_admin_repository: ITaskPromoCodeAdminRepository,
        uow: IUnitOfWork,
    ) -> UpdateTaskPromoCodeTaskHandler:
        return UpdateTaskPromoCodeTaskHandler(
            repository=task_promo_code_admin_repository,
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

    # TODO DEV: удалить get_truncate_db_handler перед релизом.
    @provide(scope=Scope.REQUEST)
    def get_truncate_db_handler(
        self,
        db_manager: IDBManager,
    ) -> TruncateDBHandler:
        return TruncateDBHandler(db_manager=db_manager)

    # TODO DEV: удалить get_seed_dev_scenario_handler перед релизом.
    @provide(scope=Scope.REQUEST)
    def get_seed_dev_scenario_handler(
        self,
        session: AsyncSession,
        vk_settings: VKSettings,
    ) -> "SeedDevScenarioHandler":
        from application.admin.command.seed_dev_scenario import SeedDevScenarioHandler

        return SeedDevScenarioHandler(session=session, vk_settings=vk_settings)
