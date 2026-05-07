from pydantic_settings import SettingsConfigDict

from settings.base import Settings


class VKSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="VK_",
        extra="ignore",
    )

    GROUP_ID: int
    GROUP_ACCESS_TOKEN: str
    CONFIRMATION_CODE: str
    SECRET_KEY: str | None = None
    API_VERSION: str = "5.199"
    API_BASE_URL: str = "https://api.vk.com/method"
    REQUEST_TIMEOUT_SECONDS: float = 5.0
    REQUIRED_SUBSCRIPTION_GROUP_ID: int | None = None

    @property
    def required_subscription_group_id(self) -> int:
        return self.REQUIRED_SUBSCRIPTION_GROUP_ID or self.GROUP_ID
