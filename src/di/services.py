from dishka import Provider, Scope, provide

from application.interface.repositories.achievements import IAchievementRepository
from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.tasks import ITaskRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository
from application.interface.services import IUserMessageIntentClassifier
from application.services.award_achievement_service import AwardAchievementService
from application.services.award_task_service import AwardTaskService
from application.services.daily_streak_achievement_service import DailyStreakAchievementService
from application.services.user_message_intent import RuleBasedUserMessageIntentClassifier
from application.services.week_completion_achievement_service import WeekCompletionAchievementService


class ServicesProvider(Provider):
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
    ) -> AwardTaskService:
        return AwardTaskService(
            users=users,
            task_completions=task_completions,
            transactions=transactions,
            week_completion_achievements=week_completion_achievements,
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
    def get_daily_streak_achievement_service(
        self,
        achievements: IAchievementRepository,
        award_achievement_service: AwardAchievementService,
    ) -> DailyStreakAchievementService:
        return DailyStreakAchievementService(
            achievements=achievements,
            award_achievement_service=award_achievement_service,
        )

    @provide(scope=Scope.APP, provides=IUserMessageIntentClassifier)
    def get_user_message_intent_classifier(self) -> RuleBasedUserMessageIntentClassifier:
        return RuleBasedUserMessageIntentClassifier()
