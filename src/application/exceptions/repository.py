from dataclasses import dataclass

from application.exceptions.base import AppException


@dataclass(frozen=True, kw_only=True)
class RepositoryError(AppException):
    @property
    def title(self) -> str:
        return "A repository error occurred"


@dataclass(frozen=True, kw_only=True)
class UserNotFoundError(RepositoryError):
    @property
    def title(self) -> str:
        return "User not found"


@dataclass(frozen=True, kw_only=True)
class PrizeNotFoundError(RepositoryError):
    @property
    def title(self) -> str:
        return "Prize not found"


@dataclass(frozen=True, kw_only=True)
class PrizeNotAvailableError(AppException):
    @property
    def title(self) -> str:
        return "Prize is not available or already sold out"


@dataclass(frozen=True, kw_only=True)
class InsufficientBalanceError(AppException):
    @property
    def title(self) -> str:
        return "Insufficient balance to redeem prize"


@dataclass(frozen=True, kw_only=True)
class TaskNotFoundError(RepositoryError):
    @property
    def title(self) -> str:
        return "Task not found"


@dataclass(frozen=True, kw_only=True)
class TaskAlreadyCompletedError(AppException):
    @property
    def title(self) -> str:
        return "Task has already been completed"


@dataclass(frozen=True, kw_only=True)
class ReferralAlreadyExistsError(AppException):
    @property
    def title(self) -> str:
        return "Referral already exists"
