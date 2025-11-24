import uuid
from dataclasses import dataclass
from typing import Protocol, Optional

from internal.core.domain.models.film import SortBy, Film
from internal.pkg.pagination import PaginatedResult, Pagination
from internal.ports.films_repository import FilmRepository, FilmSearchParams


@dataclass(kw_only=True)
class GetFilmsByParams(Pagination):
    sort: SortBy = SortBy.IMDB_RATING_DESC
    genre: Optional[uuid.UUID] = None
    person: Optional[uuid.UUID] = None


class GetFilmsByParamsHandlerProtocol(Protocol):
    async def handle(self, query: GetFilmsByParams) \
            -> PaginatedResult[Film]:
        pass


class GetFilmsByParamsHandler:
    def __init__(self, film_repository: FilmRepository) -> None:
        self.films_repository = film_repository

    async def handle(self, query: GetFilmsByParams) \
            -> PaginatedResult[Film]:
        search_params = FilmSearchParams(sort=query.sort,
                                         genre=query.genre,
                                         person=query.person,
                                         page=query.page,
                                         per_page=query.per_page)
        response = await self.films_repository.search_by_params(search_params)
        return response
