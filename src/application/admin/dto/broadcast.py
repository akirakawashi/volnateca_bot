from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class BroadcastStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True, frozen=True, kw_only=True)
class BroadcastSnapshotDTO:
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


__all__ = [
    "BroadcastSnapshotDTO",
    "BroadcastStatus",
]
