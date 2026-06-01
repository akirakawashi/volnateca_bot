from datetime import datetime

from pydantic import BaseModel, Field

from application.admin.admin_rules import ADMIN_MAX_PAGE
from application.admin.command.prize_redemption import (
    CancelPrizeRedemptionCommand,
    FulfillPrizeRedemptionCommand,
    ListPrizeRedemptionsCommand,
)
from application.admin.dto.pagination import AdminListPageDTO
from application.admin.dto.prize_redemption import PrizeRedemptionAdminDTO
from presentation.http.dto.admin.pagination import AdminListPageResponseSchema
from domain.enums.prize import PrizeReceiveType, PrizeRedemptionStatus


class ListPrizeRedemptionsQuerySchema(BaseModel):
    status: PrizeRedemptionStatus | None = None
    prizes_id: int | None = Field(default=None, ge=1)
    page: int = Field(default=1, ge=1, le=ADMIN_MAX_PAGE)

    def to_command(self) -> ListPrizeRedemptionsCommand:
        return ListPrizeRedemptionsCommand(
            status=self.status,
            prizes_id=self.prizes_id,
            page=self.page,
        )


class CancelPrizeRedemptionRequestSchema(BaseModel):
    cancel_reason: str | None = None

    def to_command(self, *, prize_redemptions_id: int) -> CancelPrizeRedemptionCommand:
        return CancelPrizeRedemptionCommand(
            prize_redemptions_id=prize_redemptions_id,
            cancel_reason=self.cancel_reason,
        )


class FulfillPrizeRedemptionRequestSchema(BaseModel):
    comment: str | None = None

    def to_command(self, *, prize_redemptions_id: int) -> FulfillPrizeRedemptionCommand:
        return FulfillPrizeRedemptionCommand(
            prize_redemptions_id=prize_redemptions_id,
            comment=self.comment,
        )


class PrizeRedemptionQueueCountResponseSchema(BaseModel):
    count: int = Field(ge=0)


class PrizeRedemptionResponseSchema(BaseModel):
    prize_redemptions_id: int
    users_id: int
    vk_user_id: int | None
    prizes_id: int
    prize_name: str
    transactions_id: int
    refund_transactions_id: int | None
    prize_redemption_status: PrizeRedemptionStatus
    receive_type: PrizeReceiveType
    redemption_code: str
    points_spent: int
    comment: str | None
    issued_at: datetime | None
    canceled_at: datetime | None
    cancel_reason: str | None
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: PrizeRedemptionAdminDTO) -> "PrizeRedemptionResponseSchema":
        return cls(
            prize_redemptions_id=dto.prize_redemptions_id,
            users_id=dto.users_id,
            vk_user_id=dto.vk_user_id,
            prizes_id=dto.prizes_id,
            prize_name=dto.prize_name,
            transactions_id=dto.transactions_id,
            refund_transactions_id=dto.refund_transactions_id,
            prize_redemption_status=dto.prize_redemption_status,
            receive_type=dto.receive_type,
            redemption_code=dto.redemption_code,
            points_spent=dto.points_spent,
            comment=dto.comment,
            issued_at=dto.issued_at,
            canceled_at=dto.canceled_at,
            cancel_reason=dto.cancel_reason,
            created_at=dto.created_at,
        )


class PrizeRedemptionsPageResponseSchema(AdminListPageResponseSchema):
    items: list[PrizeRedemptionResponseSchema]

    @classmethod
    def from_page_dto(
        cls,
        page: AdminListPageDTO[PrizeRedemptionAdminDTO],
    ) -> "PrizeRedemptionsPageResponseSchema":
        return cls(
            page=page.page,
            page_size=page.page_size,
            has_more=page.has_more,
            items=[PrizeRedemptionResponseSchema.from_dto(item) for item in page.items],
        )


__all__ = [
    "CancelPrizeRedemptionRequestSchema",
    "FulfillPrizeRedemptionRequestSchema",
    "ListPrizeRedemptionsQuerySchema",
    "PrizeRedemptionQueueCountResponseSchema",
    "PrizeRedemptionResponseSchema",
    "PrizeRedemptionsPageResponseSchema",
]
