from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request

from loguru import logger


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, pydantic_validation_error_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_error_handler)
    app.add_exception_handler(Exception, unknown_exception_handler)


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
