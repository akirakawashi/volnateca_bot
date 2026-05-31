import asyncio
from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

from loguru import logger

from application.admin.admin_rules import (
    ADMIN_BROADCAST_BATCH_SIZE,
    ADMIN_BROADCAST_SEND_CONCURRENCY,
)
from application.admin.dto.broadcast import BroadcastSnapshotDTO, BroadcastStatus
from application.admin.interface.broadcast_recipients import IBroadcastRecipientReader
from application.common.dto.user import ActiveVKUserDTO
from application.interface.clients import IVKMessageClient


class BroadcastAlreadyRunningError(RuntimeError):
    pass


class BroadcastNotFoundError(KeyError):
    pass


class BroadcastManager:
    def __init__(
        self,
        recipient_reader: IBroadcastRecipientReader,
        message_client: IVKMessageClient,
        *,
        batch_size: int = ADMIN_BROADCAST_BATCH_SIZE,
        send_concurrency: int = ADMIN_BROADCAST_SEND_CONCURRENCY,
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        if send_concurrency < 1:
            raise ValueError("send_concurrency must be positive")

        self._recipient_reader = recipient_reader
        self._message_client = message_client
        self._batch_size = batch_size
        self._send_concurrency = send_concurrency
        self._start_lock = asyncio.Lock()
        self._snapshots: dict[str, BroadcastSnapshotDTO] = {}
        self._active_broadcast_id: str | None = None
        self._active_task: asyncio.Task[None] | None = None

    async def start(self, *, message: str) -> BroadcastSnapshotDTO:
        clean_message = message.strip()
        if not clean_message:
            raise ValueError("Message must not be empty")

        async with self._start_lock:
            if self._active_broadcast_id is not None:
                snapshot = self._snapshots.get(self._active_broadcast_id)
                if snapshot is not None and snapshot.status in {BroadcastStatus.QUEUED, BroadcastStatus.RUNNING}:
                    raise BroadcastAlreadyRunningError("Broadcast is already running")

            broadcast_id = uuid4().hex
            snapshot = BroadcastSnapshotDTO(
                broadcast_id=broadcast_id,
                status=BroadcastStatus.QUEUED,
                message=clean_message,
                target_total=None,
                processed_total=0,
                sent_total=0,
                failed_total=0,
                started_at=None,
                finished_at=None,
                error=None,
            )
            self._snapshots[broadcast_id] = snapshot
            self._active_broadcast_id = broadcast_id
            self._active_task = asyncio.create_task(
                self._run_broadcast(broadcast_id=broadcast_id, message=clean_message),
                name=f"vk-broadcast-{broadcast_id}",
            )
            return snapshot

    def get_status(self, *, broadcast_id: str) -> BroadcastSnapshotDTO:
        snapshot = self._snapshots.get(broadcast_id)
        if snapshot is None:
            raise BroadcastNotFoundError(broadcast_id)
        return snapshot

    async def _run_broadcast(self, *, broadcast_id: str, message: str) -> None:
        logger.info("VK broadcast started: broadcast_id={}", broadcast_id)
        processed_total = 0
        sent_total = 0
        failed_total = 0
        last_users_id: int | None = None

        try:
            target_total = await self._recipient_reader.count_active_users()
            self._save_snapshot(
                replace(
                    self._snapshots[broadcast_id],
                    status=BroadcastStatus.RUNNING,
                    target_total=target_total,
                    started_at=datetime.now(UTC),
                ),
            )

            while True:
                recipients = await self._recipient_reader.list_active_users_page(
                    after_users_id=last_users_id,
                    limit=self._batch_size,
                )
                if not recipients:
                    break

                last_users_id = recipients[-1].users_id
                batch_sent, batch_failed = await self._send_batch(message=message, recipients=recipients)
                processed_total += len(recipients)
                sent_total += batch_sent
                failed_total += batch_failed

                self._save_snapshot(
                    replace(
                        self._snapshots[broadcast_id],
                        processed_total=processed_total,
                        sent_total=sent_total,
                        failed_total=failed_total,
                    ),
                )
                logger.info(
                    "VK broadcast progress: broadcast_id={}, processed={}, sent={}, failed={}, target={}",
                    broadcast_id,
                    processed_total,
                    sent_total,
                    failed_total,
                    target_total,
                )

            self._save_snapshot(
                replace(
                    self._snapshots[broadcast_id],
                    status=BroadcastStatus.COMPLETED,
                    finished_at=datetime.now(UTC),
                ),
            )
            logger.info(
                "VK broadcast completed: broadcast_id={}, processed={}, sent={}, failed={}",
                broadcast_id,
                processed_total,
                sent_total,
                failed_total,
            )
        except Exception as exc:
            logger.exception("VK broadcast failed: broadcast_id={}", broadcast_id)
            self._save_snapshot(
                replace(
                    self._snapshots[broadcast_id],
                    status=BroadcastStatus.FAILED,
                    error=str(exc),
                    finished_at=datetime.now(UTC),
                ),
            )
        finally:
            if self._active_broadcast_id == broadcast_id:
                self._active_broadcast_id = None
                self._active_task = None

    async def _send_batch(
        self,
        *,
        message: str,
        recipients: tuple[ActiveVKUserDTO, ...],
    ) -> tuple[int, int]:
        semaphore = asyncio.Semaphore(self._send_concurrency)

        async def send_one(recipient: ActiveVKUserDTO) -> bool:
            async with semaphore:
                try:
                    return await self._message_client.send_message(
                        vk_user_id=recipient.vk_user_id,
                        message=message,
                    )
                except Exception:
                    logger.exception(
                        "VK broadcast message failed: users_id={}, vk_user_id={}",
                        recipient.users_id,
                        recipient.vk_user_id,
                    )
                    return False

        results = await asyncio.gather(*(send_one(recipient) for recipient in recipients))
        sent_total = sum(1 for sent in results if sent)
        return sent_total, len(results) - sent_total

    def _save_snapshot(
        self,
        snapshot: BroadcastSnapshotDTO,
    ) -> BroadcastSnapshotDTO:
        self._snapshots[snapshot.broadcast_id] = snapshot
        return snapshot
