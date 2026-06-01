from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True, frozen=True, kw_only=True)
class AdminListPageDTO(Generic[T]):
    page: int
    page_size: int
    has_more: bool
    items: tuple[T, ...]


def build_admin_list_page(
    *,
    page: int,
    page_size: int,
    fetched: Sequence[T],
) -> AdminListPageDTO[T]:
    items_tuple = tuple(fetched)
    return AdminListPageDTO(
        page=page,
        page_size=page_size,
        has_more=len(items_tuple) > page_size,
        items=items_tuple[:page_size],
    )


__all__ = ["AdminListPageDTO", "build_admin_list_page"]
