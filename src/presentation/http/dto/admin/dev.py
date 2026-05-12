# TODO: удалить перед релизом — только для локальной отладки.

from pydantic import BaseModel, Field


class SeedDevScenarioRequest(BaseModel):
    scenario: str = Field(
        ...,
        description=(
            "Сценарий: daily7, daily30, quiz5, quiz-broken, "
            "week, monthly_top, project12, referral3, referral5, referral10"
        ),
    )
    users_id: int = Field(default=1, ge=1)


class AwardMonthlyTopRequest(BaseModel):
    month: str = Field(..., description="YYYY-MM")
    limit: int = Field(default=10, ge=1)


class SeedDevScenarioResponse(BaseModel):
    messages: list[str]


class AwardMonthlyTopResponse(BaseModel):
    month: str
    messages: list[str]
