from collections.abc import Awaitable, Callable
from functools import partial

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request

from application.exceptions.repository import (
    InsufficientBalanceError,
    PrizeNotAvailableError,
    PrizeNotFoundError,
    ReferralAlreadyExistsError,
    RepositoryError,
    TaskAlreadyCompletedError,
    TaskNotFoundError,
    UserNotFoundError,
)
from domain.exception import DomainValidationError
from domain.exceptions import AppError
from loguru import logger


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainValidationError, error_handler(status.HTTP_400_BAD_REQUEST))
    app.add_exception_handler(UserNotFoundError, error_handler(status.HTTP_404_NOT_FOUND))
    app.add_exception_handler(PrizeNotFoundError, error_handler(status.HTTP_404_NOT_FOUND))
    app.add_exception_handler(TaskNotFoundError, error_handler(status.HTTP_404_NOT_FOUND))
    app.add_exception_handler(PrizeNotAvailableError, error_handler(status.HTTP_409_CONFLICT))
    app.add_exception_handler(TaskAlreadyCompletedError, error_handler(status.HTTP_409_CONFLICT))
    app.add_exception_handler(ReferralAlreadyExistsError, error_handler(status.HTTP_409_CONFLICT))
    app.add_exception_handler(InsufficientBalanceError, error_handler(status.HTTP_422_UNPROCESSABLE_ENTITY))
    app.add_exception_handler(RepositoryError, error_handler(status.HTTP_500_INTERNAL_SERVER_ERROR))
    app.add_exception_handler(RequestValidationError, pydantic_validation_error_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_error_handler)
    app.add_exception_handler(AppError, error_handler(status.HTTP_500_INTERNAL_SERVER_ERROR))
    app.add_exception_handler(Exception, unknown_exception_handler)


def error_handler(status_code: int) -> Callable[..., Awaitable[JSONResponse]]:
    return partial(app_error_handler, status_code=status_code)


async def app_error_handler(
    request: Request,
    err: AppError,
    status_code: int,
) -> JSONResponse:
    logger.error("Application error: {}", err.title)
    return JSONResponse(
        status_code=status_code,
        content={"status": False, "message": err.title, "context": None},
    )


async def pydantic_validation_error_handler(
    request: Request,
    err: Exception,
) -> JSONResponse:
    if not isinstance(err, RequestValidationError | ValidationError):
        raise err

    logger.warning("Validation error: {}", err)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status": False, "message": "Validation error", "context": err.errors()},
    )


async def unknown_exception_handler(request: Request, err: Exception) -> JSONResponse:
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": False, "message": "Internal server error", "context": None},
    )
