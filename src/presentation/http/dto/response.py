from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

TData = TypeVar("TData")
TError = TypeVar("TError")


@dataclass(frozen=True)
class OkResponse(Generic[TData]):
    status: bool = True
    data: TData | None = None


@dataclass(frozen=True, kw_only=True)
class AlertResponse(Generic[TData]):
    status: bool = False
    message: str


@dataclass(frozen=True, kw_only=True)
class ErrorResponse(Generic[TError]):
    message: str
    context: TError


class ErrorValidationResponse(BaseModel):
    message: str = Field(examples=["Произошла ошибка при обработке запроса"])
    context: dict[str, Any] | list[list[dict[str, Any]]] | None = Field(
        examples=[{"detail": "Подробное описание ошибки"}],
    )


class ValidationErrorResponse(ErrorValidationResponse):
    context: list[list[dict[str, Any]]] = Field(
        examples=[
            [
                {
                    "loc": ["body", "field"],
                    "msg": "field required",
                    "type": "missing",
                },
            ],
        ],
    )


HEALTHCHECK_RESPONSE: dict[int | str, dict[str, Any]] = {
    200: {"content": {"application/json": {"example": {"status": "ok"}}}},
    500: {"content": {"application/json": {"example": {"status": "error", "detail": "string"}}}},
}
