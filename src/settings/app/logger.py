from typing import Literal

from pydantic_settings import SettingsConfigDict

from settings.base import Settings


class LoggingSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="LOG_",
        extra="ignore",
    )

    LEVEL: str = "INFO"
    FORMAT: Literal["json", "console"] = "console"
