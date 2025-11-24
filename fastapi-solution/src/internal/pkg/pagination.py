from dataclasses import dataclass
from typing import TypeVar, Generic, List

T = TypeVar("T")


@dataclass(kw_only=True)
class Pagination:
    page: int
    per_page: int


@dataclass(kw_only=True)
class PaginatedResult(Generic[T], Pagination):
    items: List[T]
    total: int
