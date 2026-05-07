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


@dataclass(slots=True, frozen=True, kw_only=True)
class VKWallPostDTO:
    owner_id: int
    post_id: int

    @property
    def external_id(self) -> str:
        return f"wall{self.owner_id}_{self.post_id}"

    @property
    def external_id_variants(self) -> tuple[str, ...]:
        variants = {
            self.external_id,
            f"{self.owner_id}_{self.post_id}",
        }
        if self.owner_id < 0:
            variants.add(f"wall{abs(self.owner_id)}_{self.post_id}")
            variants.add(f"{abs(self.owner_id)}_{self.post_id}")
        return tuple(sorted(variants))
