from dataclasses import dataclass
from typing import Protocol

from internal.core.domain.models.film import SortBy, Film
from internal.pkg.pagination import PaginatedResult, Pagination
from internal.ports.films_repository import FilmRepository, FilmQueryParams


@dataclass(kw_only=True)
class GetFilmsBySearch(Pagination):
    sort: SortBy = SortBy.IMDB_RATING_DESC
    search_query: str


class GetFilmsBySearchHandlerProtocol(Protocol):
    async def handle(self, query: GetFilmsBySearch) \
            -> PaginatedResult[Film]:
        pass


class GetFilmsBySearchHandler:
    def __init__(self, film_repository: FilmRepository) -> None:
        self.films_repository = film_repository

    async def handle(self, query: GetFilmsBySearch) \
            -> PaginatedResult[Film]:
        query_params = FilmQueryParams(sort=query.sort,
                                         query=query.search_query,
                                         page=query.page,
                                         per_page=query.per_page)
        response = await self.films_repository.search_by_query(query_params)
        return response
