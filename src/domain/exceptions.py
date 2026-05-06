from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class AppError(Exception):
    code = "A500"

    @property
    def title(self) -> str:
        return "An application error occurred"
