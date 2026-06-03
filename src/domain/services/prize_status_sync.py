from typing import Protocol

from domain.enums.prize import PrizeStatus


class PrizeStatusSyncTarget(Protocol):
    quantity_claimed: int
    quantity_total: int
    status: PrizeStatus


def apply_sold_out_status_from_quantities(*, prize: PrizeStatusSyncTarget) -> None:
    """Синхронизирует status приза с остатком после покупки, отмены или admin PATCH.

    Ручной статус hidden не перезаписывается в sold_out, даже если остаток исчерпан.
    """

    if prize.quantity_claimed >= prize.quantity_total:
        if prize.status != PrizeStatus.HIDDEN:
            prize.status = PrizeStatus.SOLD_OUT
    elif prize.status == PrizeStatus.SOLD_OUT:
        prize.status = PrizeStatus.AVAILABLE


__all__ = [
    "PrizeStatusSyncTarget",
    "apply_sold_out_status_from_quantities",
]
