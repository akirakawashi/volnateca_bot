from typing import ClassVar

from settings.base import Settings


class CorsSettings(Settings):
    CORS_ALLOW_ORIGINS: ClassVar[list[str]] = ["*"]
    CORS_ALLOW_METHODS: ClassVar[list[str]] = ["*"]
    CORS_ALLOW_HEADERS: ClassVar[list[str]] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = False
