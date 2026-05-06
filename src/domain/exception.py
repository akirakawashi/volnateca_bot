from dataclasses import dataclass

from domain.exceptions import AppError


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
