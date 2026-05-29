# TODO: удалить перед релизом — только для локальной отладки.

from pydantic import BaseModel, Field


class SeedDevScenarioRequest(BaseModel):
    scenario: str = Field(
        ...,
        description=(
            "Сценарий: week, monthly_top, project12, referral3, referral5, referral10"
        ),
    )
    users_id: int = Field(default=1, ge=1)


class SeedDevScenarioResponse(BaseModel):
    messages: list[str]


class SeedStorePrizesResponse(BaseModel):
    messages: list[str]
