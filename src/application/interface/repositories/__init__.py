from application.interface.repositories.achievements import AchievementRecord, IAchievementRepository
from application.interface.repositories.message_templates import IMessageTemplateRepository
from application.interface.repositories.prize_promo_codes import IPrizePromoCodeRepository
from application.interface.repositories.prizes import IPrizeRepository
from application.interface.repositories.quiz import IQuizRepository
from application.interface.repositories.referral_intents import IReferralIntentRepository
from application.interface.repositories.referrals import IReferralRepository
from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.task_promo_code_waits import ITaskPromoCodeWaitRepository
from application.interface.repositories.task_promo_codes import ITaskPromoCodeRepository
from application.interface.repositories.tasks import ITaskRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository

__all__ = [
    "AchievementRecord",
    "IAchievementRepository",
    "IMessageTemplateRepository",
    "IPrizePromoCodeRepository",
    "IPrizeRepository",
    "IQuizRepository",
    "IReferralIntentRepository",
    "IReferralRepository",
    "ITaskCompletionRepository",
    "ITaskPromoCodeRepository",
    "ITaskPromoCodeWaitRepository",
    "ITaskRepository",
    "ITransactionRepository",
    "IUserRepository",
]
