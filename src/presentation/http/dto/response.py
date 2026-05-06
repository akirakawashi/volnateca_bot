from dataclasses import dataclass
from typing import Generic, TypeVar

TData = TypeVar("TData")


@dataclass(frozen=True)
class OkResponse(Generic[TData]):
    status: bool = True
    data: TData | None = None
