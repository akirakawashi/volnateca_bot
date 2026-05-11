from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class AppError(Exception):
    code = "A500"

    @property
    def title(self) -> str:
        return "Произошла ошибка приложения"


@dataclass(frozen=True, kw_only=True)
class DomainError(AppError):
    @property
    def title(self) -> str:
        return "Произошла доменная ошибка"


@dataclass(frozen=True, kw_only=True)
class DomainValidationError(DomainError):
    @property
    def title(self) -> str:
        return "Произошла ошибка проверки доменного правила"


@dataclass(frozen=True, kw_only=True)
class DomainNotFoundError(DomainError):
    @property
    def title(self) -> str:
        return "Доменная сущность не найдена"


@dataclass(frozen=True, kw_only=True)
class UserNotFoundError(DomainNotFoundError):
    @property
    def title(self) -> str:
        return "Пользователь не найден"


@dataclass(frozen=True, kw_only=True)
class PrizeNotFoundError(DomainNotFoundError):
    @property
    def title(self) -> str:
        return "Приз не найден"


@dataclass(frozen=True, kw_only=True)
class TaskNotFoundError(DomainNotFoundError):
    @property
    def title(self) -> str:
        return "Задание не найдено"


@dataclass(frozen=True, kw_only=True)
class PrizeNotAvailableError(DomainValidationError):
    @property
    def title(self) -> str:
        return "Приз недоступен или уже разобран"


@dataclass(frozen=True, kw_only=True)
class InsufficientBalanceError(DomainValidationError):
    @property
    def title(self) -> str:
        return "Недостаточно баллов для получения приза"


@dataclass(frozen=True, kw_only=True)
class TaskAlreadyCompletedError(DomainValidationError):
    @property
    def title(self) -> str:
        return "Задание уже выполнено"


@dataclass(frozen=True, kw_only=True)
class ReferralAlreadyExistsError(DomainValidationError):
    @property
    def title(self) -> str:
        return "Реферальная связь уже существует"


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
