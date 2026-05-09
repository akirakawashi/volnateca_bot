from typing import Any


HEALTHCHECK_RESPONSE: dict[int | str, dict[str, Any]] = {
    200: {"content": {"application/json": {"example": {"status": "ok"}}}},
    500: {"content": {"application/json": {"example": {"status": "error", "detail": "string"}}}},
}
