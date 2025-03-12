from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass(frozen=True, slots=True)
class PaginateDTO:
    page: int
    limit: int

@dataclass(frozen=True, slots=True)
class PaginateOutputDTO(Generic[T]):
    page: int
    limit: int
    total: int
    total_page: int
    data: list[T]

def calculate_total_pages(total: int, limit: int) -> int: ...
