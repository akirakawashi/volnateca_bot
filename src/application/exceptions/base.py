from dataclasses import dataclass

from domain.exceptions import AppError


@dataclass(frozen=True, kw_only=True)
class AppException(AppError): ...
