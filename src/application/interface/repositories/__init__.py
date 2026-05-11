from application.interface.repositories.achievements import AchievementRecord, IAchievementRepository
from application.interface.repositories.quiz import IQuizRepository
from application.interface.repositories.referrals import IReferralRepository
from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.tasks import ITaskRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository

__all__ = [
    "AchievementRecord",
    "IAchievementRepository",
    "IQuizRepository",
    "IReferralRepository",
    "ITaskCompletionRepository",
    "ITaskRepository",
    "ITransactionRepository",
    "IUserRepository",
]
