from typing import Literal

from settings.base import Settings


class LoggingSettings(Settings):
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "console"
