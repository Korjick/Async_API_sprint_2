from dataclasses import dataclass
from typing import Protocol, Optional

from content_api.internal.core.domain.models.film import SortBy, Film
from content_api.internal.pkg.pagination import Pagination, PaginatedResult


@dataclass(kw_only=True)
class GetFilmsBySearch(Pagination):
    sort: SortBy = SortBy.IMDB_RATING_DESC
    search_query: str


class FilmsBySearchHandlerProtocol(Protocol):
    async def handle(self, query: GetFilmsBySearch) -> PaginatedResult[Film]:
        pass


instance: Optional[FilmsBySearchHandlerProtocol] = None


def get_instance() -> FilmsBySearchHandlerProtocol:
    if instance is None:
        raise RuntimeError("Films by search handler is not initialized")
    return instance
