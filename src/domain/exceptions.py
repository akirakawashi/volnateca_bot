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
