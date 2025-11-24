import uuid
from dataclasses import dataclass
from typing import Protocol, Optional, List

from internal.core.domain.models.film import SortBy, Film
from internal.pkg.pagination import PaginatedResult, Pagination


@dataclass(kw_only=True)
class FilmSearchParams(Pagination):
    sort: SortBy = SortBy.IMDB_RATING_DESC
    genre: Optional[uuid.UUID] = None
    person: Optional[uuid.UUID] = None


@dataclass(kw_only=True)
class FilmQueryParams(Pagination):
    sort: SortBy = SortBy.IMDB_RATING_DESC
    query: str


class FilmRepository(Protocol):
    async def search_by_params(self, search_params: FilmSearchParams) \
            -> PaginatedResult[Film]:
        pass

    async def search_by_query(self, query_params: FilmQueryParams) \
            -> PaginatedResult[Film]:
        pass

    async def get_film_by_id(self, film_id: uuid.UUID) -> Film:
        pass
