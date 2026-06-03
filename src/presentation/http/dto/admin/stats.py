from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from application.admin.command.stats import (
    GetDailyAccrualPointsStatsCommand,
    GetDailyActivityStatsCommand,
    GetDailyNewUsersStatsCommand,
)
from application.admin.dto.stats import (
    DailyAccrualPointsStatsDTO,
    DailyActivityStatsDTO,
    DailyNewUsersStatsDTO,
    DailyStatPointDTO,
)


class DailyActivityStatsQuerySchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_date: date | None = Field(default=None, alias="from")
    to_date: date | None = Field(default=None, alias="to")
    days: int | None = Field(default=None, ge=1, le=90)

    def to_activity_command(self) -> GetDailyActivityStatsCommand:
        return GetDailyActivityStatsCommand(
            from_date=self.from_date,
            to_date=self.to_date,
            days=self.days,
        )

    def to_new_users_command(self) -> GetDailyNewUsersStatsCommand:
        return GetDailyNewUsersStatsCommand(
            from_date=self.from_date,
            to_date=self.to_date,
            days=self.days,
        )

    def to_accrual_points_command(self) -> GetDailyAccrualPointsStatsCommand:
        return GetDailyAccrualPointsStatsCommand(
            from_date=self.from_date,
            to_date=self.to_date,
            days=self.days,
        )


class DailyStatPointResponseSchema(BaseModel):
    date: date
    value: int

    @classmethod
    def from_dto(cls, dto: DailyStatPointDTO) -> "DailyStatPointResponseSchema":
        return cls(date=dto.day, value=dto.value)


class DailyActivityStatsResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    timezone: str
    from_date: date = Field(serialization_alias="from")
    to_date: date = Field(serialization_alias="to")
    metric: str = "active_users"
    label: str = "Активные пользователи"
    description: str = (
        "Уникальные пользователи с хотя бы одним начислением баллов за календарный день"
    )
    points: list[DailyStatPointResponseSchema]

    @classmethod
    def from_dto(cls, dto: DailyActivityStatsDTO) -> "DailyActivityStatsResponseSchema":
        return cls(
            timezone=dto.timezone,
            from_date=dto.from_date,
            to_date=dto.to_date,
            points=[DailyStatPointResponseSchema.from_dto(point) for point in dto.points],
        )


class DailyNewUsersStatsResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    timezone: str
    from_date: date = Field(serialization_alias="from")
    to_date: date = Field(serialization_alias="to")
    metric: str = "new_users"
    label: str = "Новые участники"
    description: str = "Число регистраций в боте за календарный день"
    points: list[DailyStatPointResponseSchema]

    @classmethod
    def from_dto(cls, dto: DailyNewUsersStatsDTO) -> "DailyNewUsersStatsResponseSchema":
        return cls(
            timezone=dto.timezone,
            from_date=dto.from_date,
            to_date=dto.to_date,
            points=[DailyStatPointResponseSchema.from_dto(point) for point in dto.points],
        )


class DailyAccrualPointsStatsResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    timezone: str
    from_date: date = Field(serialization_alias="from")
    to_date: date = Field(serialization_alias="to")
    metric: str = "accrual_points"
    label: str = "Начислено баллов"
    description: str = "Сумма всех начислений баллов за календарный день"
    points: list[DailyStatPointResponseSchema]

    @classmethod
    def from_dto(cls, dto: DailyAccrualPointsStatsDTO) -> "DailyAccrualPointsStatsResponseSchema":
        return cls(
            timezone=dto.timezone,
            from_date=dto.from_date,
            to_date=dto.to_date,
            points=[DailyStatPointResponseSchema.from_dto(point) for point in dto.points],
        )


__all__ = [
    "DailyAccrualPointsStatsResponseSchema",
    "DailyActivityStatsQuerySchema",
    "DailyActivityStatsResponseSchema",
    "DailyNewUsersStatsResponseSchema",
    "DailyStatPointResponseSchema",
]
