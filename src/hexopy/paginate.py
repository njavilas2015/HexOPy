from typing import Callable, Generic, List
from dataclasses import dataclass
from .types import T, U


@dataclass(frozen=True, slots=True)
class Paginate(Generic[T]):
    page: int
    limit: int
    total: int
    total_page: int
    data: T


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
