from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from settings.base import Settings


class AppSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    DEBUG: bool = False
    NAME: str = "volnateca-bot"
    VERSION: str = "0.1.0"
    PROJECT_TIMEZONE: str = "Europe/Moscow"
    ADMIN_LOGIN: str = Field(min_length=1)
    ADMIN_PASSWORD: str = Field(min_length=1)
    ADMIN_TOKEN: str = Field(min_length=1)
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    @property
    def project_timezone(self) -> ZoneInfo:
        return ZoneInfo(self.PROJECT_TIMEZONE)

    @property
    def allowed_hosts(self) -> list[str]:
        return [item.strip() for item in self.ALLOWED_HOSTS.split(",") if item.strip()]
