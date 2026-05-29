from datetime import datetime

from pydantic import BaseModel, Field

from application.command.award_monthly_top import MonthlyTopAward, MonthlyTopAwardStatus


class AwardMonthlyTopRequestSchema(BaseModel):
    month: str = Field(..., description="YYYY-MM")
    limit: int = Field(default=10, ge=1)


class MonthlyTopAwardResponseSchema(BaseModel):
    rank: int
    users_id: int
    vk_user_id: int
    monthly_points: int
    status: MonthlyTopAwardStatus
    points_awarded: int
    balance_points: int | None
    level_up: int | None
    message_sent: bool

    @classmethod
    def from_award(
        cls,
        *,
        award: MonthlyTopAward,
        message_sent: bool,
    ) -> "MonthlyTopAwardResponseSchema":
        return cls(
            rank=award.rank,
            users_id=award.users_id,
            vk_user_id=award.vk_user_id,
            monthly_points=award.monthly_points,
            status=award.status,
            points_awarded=award.points_awarded,
            balance_points=award.balance_points,
            level_up=award.level_up,
            message_sent=message_sent,
        )


class AwardMonthlyTopResponseSchema(BaseModel):
    month: str
    period_start_at: datetime
    period_end_at: datetime
    achievement_found: bool
    awards: list[MonthlyTopAwardResponseSchema]
