import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from application.admin.command.task_promo_code import CreateTaskPromoCodeTaskCommand
from application.admin.dto.task_promo_code import CreatedTaskPromoCodeTaskDTO
from application.common.dto.task_promo_code import normalize_task_promo_code
from domain.enums.task import TaskRepeatPolicy


class CreateTaskPromoCodeTaskRequestSchema(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=255)
    task_name: str = Field(min_length=1, max_length=500)
    description: str | None = None
    points: int = Field(gt=0)
    week_number: int | None = Field(default=None, ge=1, le=12)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    repeat_policy: TaskRepeatPolicy = TaskRepeatPolicy.ONCE
    promo_code: str = Field(min_length=1)

    @field_validator("code", "task_name", mode="before")
    @classmethod
    def normalize_required_strings(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("description", mode="before")
    @classmethod
    def normalize_optional_strings(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value

    @field_validator("promo_code", mode="after")
    @classmethod
    def normalize_promo_code(cls, value: str) -> str:
        normalized = normalize_task_promo_code(value)
        if not normalized:
            raise ValueError("promo_code должен быть непустым")
        return normalized

    @model_validator(mode="after")
    def validate_dates(self) -> "CreateTaskPromoCodeTaskRequestSchema":
        if self.starts_at is not None and self.ends_at is not None:
            if self.starts_at >= self.ends_at:
                raise ValueError("starts_at должно быть раньше ends_at")
        if self.repeat_policy != TaskRepeatPolicy.ONCE:
            raise ValueError("Промокодное задание можно создать только с repeat_policy=once")
        return self

    def to_command(self) -> CreateTaskPromoCodeTaskCommand:
        return CreateTaskPromoCodeTaskCommand(
            code=self.code or str(uuid.uuid4()),
            task_name=self.task_name,
            description=self.description,
            points=self.points,
            week_number=self.week_number,
            starts_at=self.starts_at,
            ends_at=self.ends_at,
            repeat_policy=self.repeat_policy,
            promo_code=self.promo_code,
        )


class CreatedTaskPromoCodeTaskResponseSchema(BaseModel):
    tasks_id: int
    code: str
    task_name: str
    promo_code: str

    @classmethod
    def from_dto(cls, dto: CreatedTaskPromoCodeTaskDTO) -> "CreatedTaskPromoCodeTaskResponseSchema":
        return cls(
            tasks_id=dto.tasks_id,
            code=dto.code,
            task_name=dto.task_name,
            promo_code=dto.promo_code,
        )
