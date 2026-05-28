from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from application.admin.dto.broadcast import BroadcastSnapshotDTO, BroadcastStatus


class BroadcastStartRequestSchema(BaseModel):
    message: str = Field(min_length=1, max_length=4096)

    @field_validator("message")
    @classmethod
    def normalize_message(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Сообщение не должно быть пустым")
        return stripped


class BroadcastStartResponseSchema(BaseModel):
    broadcast_id: str
    status: BroadcastStatus
    message: str
    target_total: int | None

    @classmethod
    def from_dto(cls, dto: BroadcastSnapshotDTO) -> "BroadcastStartResponseSchema":
        return cls(
            broadcast_id=dto.broadcast_id,
            status=dto.status,
            message=dto.message,
            target_total=dto.target_total,
        )


class BroadcastStatusResponseSchema(BaseModel):
    broadcast_id: str
    status: BroadcastStatus
    message: str
    target_total: int | None
    processed_total: int
    sent_total: int
    failed_total: int
    started_at: datetime | None
    finished_at: datetime | None
    error: str | None

    @classmethod
    def from_dto(cls, dto: BroadcastSnapshotDTO) -> "BroadcastStatusResponseSchema":
        return cls(
            broadcast_id=dto.broadcast_id,
            status=dto.status,
            message=dto.message,
            target_total=dto.target_total,
            processed_total=dto.processed_total,
            sent_total=dto.sent_total,
            failed_total=dto.failed_total,
            started_at=dto.started_at,
            finished_at=dto.finished_at,
            error=dto.error,
        )
