from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class AppError(Exception):
    code = "A500"

    @property
    def title(self) -> str:
        return "An application error occurred"


@dataclass(frozen=True, kw_only=True)
class DomainError(AppError):
    @property
    def title(self) -> str:
        return "A domain error occurred"


@dataclass(frozen=True, kw_only=True)
class DomainValidationError(DomainError):
    @property
    def title(self) -> str:
        return "A domain validation error occurred"


@dataclass(frozen=True, kw_only=True)
class DomainNotFoundError(DomainError):
    @property
    def title(self) -> str:
        return "Domain entity not found"


@dataclass(frozen=True, kw_only=True)
class UserNotFoundError(DomainNotFoundError):
    @property
    def title(self) -> str:
        return "User not found"


@dataclass(frozen=True, kw_only=True)
class PrizeNotFoundError(DomainNotFoundError):
    @property
    def title(self) -> str:
        return "Prize not found"


@dataclass(frozen=True, kw_only=True)
class TaskNotFoundError(DomainNotFoundError):
    @property
    def title(self) -> str:
        return "Task not found"


@dataclass(frozen=True, kw_only=True)
class PrizeNotAvailableError(DomainValidationError):
    @property
    def title(self) -> str:
        return "Prize is not available or already sold out"


@dataclass(frozen=True, kw_only=True)
class InsufficientBalanceError(DomainValidationError):
    @property
    def title(self) -> str:
        return "Insufficient balance to redeem prize"


@dataclass(frozen=True, kw_only=True)
class TaskAlreadyCompletedError(DomainValidationError):
    @property
    def title(self) -> str:
        return "Task has already been completed"


@dataclass(frozen=True, kw_only=True)
class ReferralAlreadyExistsError(DomainValidationError):
    @property
    def title(self) -> str:
        return "Referral already exists"


__all__ = [
    "AppError",
    "DomainError",
    "DomainNotFoundError",
    "DomainValidationError",
    "InsufficientBalanceError",
    "PrizeNotAvailableError",
    "PrizeNotFoundError",
    "ReferralAlreadyExistsError",
    "TaskAlreadyCompletedError",
    "TaskNotFoundError",
    "UserNotFoundError",
]
