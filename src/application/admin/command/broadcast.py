from dataclasses import dataclass

from application.admin.dto.broadcast import BroadcastSnapshotDTO
from application.admin.services import BroadcastManager
from application.base_interactor import Interactor


@dataclass(slots=True, frozen=True, kw_only=True)
class StartBroadcastCommand:
    message: str


@dataclass(slots=True, frozen=True, kw_only=True)
class GetBroadcastStatusCommand:
    broadcast_id: str


class StartBroadcastHandler(Interactor[StartBroadcastCommand, BroadcastSnapshotDTO]):
    def __init__(self, broadcast_manager: BroadcastManager) -> None:
        self._broadcast_manager = broadcast_manager

    async def __call__(self, command_data: StartBroadcastCommand) -> BroadcastSnapshotDTO:
        return await self._broadcast_manager.start(message=command_data.message)


class GetBroadcastStatusHandler(Interactor[GetBroadcastStatusCommand, BroadcastSnapshotDTO]):
    def __init__(self, broadcast_manager: BroadcastManager) -> None:
        self._broadcast_manager = broadcast_manager

    async def __call__(self, command_data: GetBroadcastStatusCommand) -> BroadcastSnapshotDTO:
        return self._broadcast_manager.get_status(broadcast_id=command_data.broadcast_id)


__all__ = [
    "GetBroadcastStatusCommand",
    "GetBroadcastStatusHandler",
    "StartBroadcastCommand",
    "StartBroadcastHandler",
]
