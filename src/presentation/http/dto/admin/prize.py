from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

from application.admin.admin_rules import ADMIN_ALLOWED_PRIZE_TYPES, ADMIN_ALLOWED_RECEIVE_TYPES
from application.admin.dto.prize import CreatePrizeCommand, PrizeAdminDTO, UpdatePrizeCommand
from domain.enums.prize import PrizeReceiveType, PrizeStatus, PrizeType
from utils.vk_attachments import normalize_vk_photo_attachment


class CreatePrizeRequestSchema(BaseModel):
    prize_name: str = Field(min_length=1, max_length=500)
    description: str | None = None
    image_attachment: str | None = None
    prize_type: PrizeType
    receive_type: PrizeReceiveType
    status: PrizeStatus = PrizeStatus.AVAILABLE
    cost_points: int = Field(gt=0)
    quantity_total: int = Field(ge=1)
    required_level: int | None = Field(default=None, ge=1, le=4)
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = True

    @field_validator("prize_name", mode="before")
    @classmethod
    def normalize_prize_name(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("description", "image_attachment", mode="before")
    @classmethod
    def normalize_optional_strings(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value

    @field_validator("image_attachment")
    @classmethod
    def validate_image_attachment(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = normalize_vk_photo_attachment(value)
        if normalized is None:
            raise ValueError("image_attachment должен быть в формате photo-123_456")
        return normalized

    @field_validator("prize_type")
    @classmethod
    def validate_prize_type(cls, value: PrizeType) -> PrizeType:
        if value not in ADMIN_ALLOWED_PRIZE_TYPES:
            raise ValueError("Поддерживаются только merch, partner и super_prize")
        return value

    @field_validator("receive_type")
    @classmethod
    def validate_receive_type(cls, value: PrizeReceiveType) -> PrizeReceiveType:
        if value not in ADMIN_ALLOWED_RECEIVE_TYPES:
            raise ValueError("Поддерживается только receive_type pickup")
        return value

    def to_command(self) -> CreatePrizeCommand:
        return CreatePrizeCommand(
            prize_name=self.prize_name,
            description=self.description,
            image_attachment=self.image_attachment,
            prize_type=self.prize_type,
            receive_type=self.receive_type,
            status=self.status,
            cost_points=self.cost_points,
            quantity_total=self.quantity_total,
            required_level=self.required_level,
            sort_order=self.sort_order,
            is_active=self.is_active,
        )


class UpdatePrizeRequestSchema(BaseModel):
    prize_name: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    image_attachment: str | None = None
    status: PrizeStatus | None = None
    cost_points: int | None = Field(default=None, gt=0)
    quantity_total: int | None = Field(default=None, ge=1)
    required_level: int | None = Field(default=None, ge=1, le=4)
    sort_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @field_validator("prize_name", mode="before")
    @classmethod
    def normalize_prize_name(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("description", "image_attachment", mode="before")
    @classmethod
    def normalize_optional_strings(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value

    @field_validator("image_attachment")
    @classmethod
    def validate_image_attachment(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = normalize_vk_photo_attachment(value)
        if normalized is None:
            raise ValueError("image_attachment должен быть в формате photo-123_456")
        return normalized

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Нужно передать хотя бы одно поле для обновления")
        return self

    def to_command(self, *, prizes_id: int) -> UpdatePrizeCommand:
        fields = frozenset(self.model_fields_set)
        return UpdatePrizeCommand(
            prizes_id=prizes_id,
            fields=fields,
            prize_name=self.prize_name,
            description=self.description,
            image_attachment=self.image_attachment,
            status=self.status,
            cost_points=self.cost_points,
            quantity_total=self.quantity_total,
            required_level=self.required_level,
            sort_order=self.sort_order,
            is_active=self.is_active,
        )


class PrizeResponseSchema(BaseModel):
    prizes_id: int
    code: str
    prize_name: str
    description: str | None
    image_attachment: str | None
    prize_type: PrizeType
    receive_type: PrizeReceiveType
    status: PrizeStatus
    cost_points: int
    quantity_total: int
    quantity_claimed: int
    required_level: int | None
    sort_order: int
    is_active: bool

    @classmethod
    def from_dto(cls, dto: PrizeAdminDTO) -> "PrizeResponseSchema":
        return cls(
            prizes_id=dto.prizes_id,
            code=dto.code,
            prize_name=dto.prize_name,
            description=dto.description,
            image_attachment=dto.image_attachment,
            prize_type=dto.prize_type,
            receive_type=dto.receive_type,
            status=dto.status,
            cost_points=dto.cost_points,
            quantity_total=dto.quantity_total,
            quantity_claimed=dto.quantity_claimed,
            required_level=dto.required_level,
            sort_order=dto.sort_order,
            is_active=dto.is_active,
        )


__all__ = [
    "CreatePrizeRequestSchema",
    "PrizeResponseSchema",
    "UpdatePrizeRequestSchema",
]
