from typing import Generic, TypeVar

T = TypeVar("T")

class PaginateDTO:
    page: int
    limit: int

class PaginateOutputDTO(Generic[T]):
    page: int
    limit: int
    total: int
    total_page: int
    data: list[T]

def calculate_total_pages(total: int, limit: int) -> int: ...
