from typing import Literal

from pydantic_settings import SettingsConfigDict

from settings.base import Settings


class LoggingSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="LOG_")

    LEVEL: str = "INFO"
    FORMAT: Literal["json", "console"] = "console"
