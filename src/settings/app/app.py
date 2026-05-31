from zoneinfo import ZoneInfo

from pydantic import Field, field_validator
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
    ADMIN_SESSION_SECRET: str = Field(min_length=32)
    ADMIN_SESSION_TTL_SECONDS: int = Field(default=7200, ge=60)
    ADMIN_SESSION_COOKIE_SECURE: bool = True
    ADMIN_SESSION_COOKIE_SAMESITE: str = "lax"
    ALLOWED_HOSTS: str = Field(min_length=1)

    @field_validator("ADMIN_SESSION_COOKIE_SAMESITE")
    @classmethod
    def validate_admin_session_cookie_samesite(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {"lax", "strict", "none"}:
            raise ValueError("APP_ADMIN_SESSION_COOKIE_SAMESITE must be one of: lax, strict, none")
        return normalized

    @field_validator("ALLOWED_HOSTS")
    @classmethod
    def validate_allowed_hosts(cls, value: str) -> str:
        if not any(item.strip() for item in value.split(",")):
            raise ValueError("APP_ALLOWED_HOSTS must contain at least one host")
        return value

    @property
    def project_timezone(self) -> ZoneInfo:
        return ZoneInfo(self.PROJECT_TIMEZONE)

    @property
    def allowed_hosts(self) -> list[str]:
        return [item.strip() for item in self.ALLOWED_HOSTS.split(",") if item.strip()]
