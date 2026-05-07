from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class VKUserProfileDTO:
    vk_user_id: int
    first_name: str | None
    last_name: str | None
    screen_name: str | None = None

    @property
    def stable_profile_url(self) -> str:
        return f"https://vk.com/id{self.vk_user_id}"

    @property
    def profile_url(self) -> str:
        if self.screen_name:
            return f"https://vk.com/{self.screen_name}"
        return self.stable_profile_url
