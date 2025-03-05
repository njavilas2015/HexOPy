from typing import Callable, Generic, List

from pydantic import field_validator
from pydantic.dataclasses import dataclass

from onbbu.types import T, U


@dataclass(frozen=True, slots=True)
class PaginateDTO:
    page: int
    limit: int

    @field_validator("page")
    def validate_page(cls, v: int):
        if v <= 0:
            raise ValueError("Page must be a positive integer")
        return v

    @field_validator("limit")
    def validate_limit(cls, v: int):
        if v <= 0:
            raise ValueError("Limit must be a positive integer")
        return v


@dataclass(frozen=True, slots=True)
class Paginate(Generic[T]):
    page: int
    limit: int
    total: int
    total_page: int
    data: T

    @staticmethod
    def calculate_total_pages(total: int, limit: int) -> int:
        return (total // limit) + (1 if total % limit > 0 else 0)


def createPaginateResponse(
    paginate: Paginate[T], transformFunc: Callable[[List[T]], List[U]]
):

    return Paginate(
        page=paginate.page,
        limit=paginate.limit,
        total=paginate.total,
        total_page=paginate.total_page,
        data=transformFunc(paginate.data),
    )
