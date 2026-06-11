from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

from application.admin.admin_rules import ADMIN_ALLOWED_PRIZE_TYPES, ADMIN_ALLOWED_RECEIVE_TYPES
from application.admin.command.prize import CreatePrizeCommand, UpdatePrizeCommand
from application.admin.command.prize_promo_code import AddPrizePromoCodesCommand
from application.admin.dto.prize import PrizeAdminDTO
from application.common.dto.prize_promo_code import normalize_prize_promo_codes
from domain.enums.prize import PrizeReceiveType, PrizeStatus, PrizeType
from utils.vk_attachments import normalize_vk_photo_attachment


class CreatePrizeRequestSchema(BaseModel):
    prize_name: str = Field(min_length=1, max_length=500)
    description: str | None = None
    image_attachment: str | None = None
    prize_type: PrizeType
    receive_type: PrizeReceiveType | None = None
    status: PrizeStatus = PrizeStatus.AVAILABLE
    cost_points: int = Field(gt=0)
    quantity_total: int | None = Field(default=None, ge=1)
    required_level: int | None = Field(default=None, ge=1, le=4)
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = True
    promo_codes: tuple[str, ...] = ()

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
    def validate_receive_type(cls, value: PrizeReceiveType | None) -> PrizeReceiveType | None:
        if value is None:
            return value
        if value not in ADMIN_ALLOWED_RECEIVE_TYPES:
            raise ValueError("Поддерживаются только receive_type pickup и promo_code")
        return value

    @model_validator(mode="after")
    def validate_type_specific_fields(self) -> Self:
        if self.prize_type == PrizeType.PARTNER:
            promo_codes = normalize_prize_promo_codes(self.promo_codes)
            if self.status == PrizeStatus.AVAILABLE and not promo_codes:
                raise ValueError("Для доступного партнёрского приза нужно загрузить хотя бы один промокод")
            return self

        if self.quantity_total is None:
            raise ValueError("quantity_total обязателен для мерча и суперпризов")
        return self

    def to_command(self) -> CreatePrizeCommand:
        promo_codes = normalize_prize_promo_codes(self.promo_codes)
        is_partner = self.prize_type == PrizeType.PARTNER
        return CreatePrizeCommand(
            prize_name=self.prize_name,
            description=self.description,
            image_attachment=self.image_attachment,
            prize_type=self.prize_type,
            receive_type=PrizeReceiveType.PROMO_CODE if is_partner else PrizeReceiveType.PICKUP,
            status=self.status,
            cost_points=self.cost_points,
            quantity_total=(max(1, len(promo_codes)) if is_partner else self.quantity_total or 1),
            required_level=self.required_level,
            sort_order=self.sort_order,
            is_active=self.is_active,
            promo_codes=promo_codes,
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


class AddPrizePromoCodesRequestSchema(BaseModel):
    promo_codes: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_codes(self) -> Self:
        if not normalize_prize_promo_codes(self.promo_codes):
            raise ValueError("Нужно передать хотя бы один непустой промокод")
        return self

    def to_command(self, *, prizes_id: int) -> AddPrizePromoCodesCommand:
        return AddPrizePromoCodesCommand(
            prizes_id=prizes_id,
            promo_codes=self.promo_codes,
        )


class AddPrizePromoCodesResponseSchema(BaseModel):
    prizes_id: int
    created: int = Field(ge=0)
    duplicates: int = Field(ge=0)
    total_codes: int = Field(ge=0)
    available_codes: int = Field(ge=0)
    assigned_codes: int = Field(ge=0)
    void_codes: int = Field(ge=0)


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

    promo_codes_total: int | None = None
    promo_codes_available: int | None = None
    promo_codes_assigned: int | None = None
    promo_codes_void: int | None = None

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
            promo_codes_total=dto.promo_codes_total,
            promo_codes_available=dto.promo_codes_available,
            promo_codes_assigned=dto.promo_codes_assigned,
            promo_codes_void=dto.promo_codes_void,
        )


__all__ = [
    "AddPrizePromoCodesRequestSchema",
    "AddPrizePromoCodesResponseSchema",
    "CreatePrizeRequestSchema",
    "PrizeResponseSchema",
    "UpdatePrizeRequestSchema",
]
