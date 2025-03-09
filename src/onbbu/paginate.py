from typing import Generic, List, TypeVar

from pydantic import Field
from pydantic.dataclasses import dataclass

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class PaginateDTO:
    page: int = Field(alias="page", ge=1)
    limit: int = Field(alias="limit", ge=1)


@dataclass(frozen=True, slots=True)
class PaginateOutputDTO(Generic[T]):
    page: int
    limit: int
    total: int
    total_page: int
    data: List[T]


def calculate_total_pages(total: int, limit: int) -> int:
    return (total // limit) + (1 if total % limit > 0 else 0)
