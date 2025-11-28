import uuid
from dataclasses import dataclass
from typing import Optional, Protocol

from internal.core.domain.models.film import SortBy, Film
from internal.pkg.pagination import Pagination, PaginatedResult


@dataclass(kw_only=True)
class GetFilmsByParams(Pagination):
    sort: SortBy = SortBy.IMDB_RATING_DESC
    genre: Optional[uuid.UUID] = None
    person: Optional[uuid.UUID] = None


class FilmsByParamsHandlerProtocol(Protocol):
    async def handle(self, query: GetFilmsByParams) -> PaginatedResult[Film]:
        pass


instance: Optional[FilmsByParamsHandlerProtocol] = None


def get_instance() -> FilmsByParamsHandlerProtocol:
    if instance is None:
        raise RuntimeError("Films by params handler is not initialized")
    return instance
