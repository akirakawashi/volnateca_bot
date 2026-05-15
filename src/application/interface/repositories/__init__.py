from application.interface.repositories.achievements import AchievementRecord, IAchievementRepository
from application.interface.repositories.message_templates import IMessageTemplateRepository
from application.interface.repositories.quiz import IQuizRepository
from application.interface.repositories.referrals import IReferralRepository
from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.tasks import ITaskRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.user_daily_activities import (
    IUserDailyActivityRepository,
    UserDailyActivityRecord,
)
from application.interface.repositories.users import IUserRepository

__all__ = [
    "AchievementRecord",
    "IAchievementRepository",
    "IMessageTemplateRepository",
    "IUserDailyActivityRepository",
    "IQuizRepository",
    "IReferralRepository",
    "ITaskCompletionRepository",
    "ITaskRepository",
    "ITransactionRepository",
    "UserDailyActivityRecord",
    "IUserRepository",
]
