from application.interface.repositories.quiz import IQuizRepository
from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.tasks import ITaskRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository

__all__ = [
    "IQuizRepository",
    "ITaskCompletionRepository",
    "ITaskRepository",
    "ITransactionRepository",
    "IUserRepository",
]
