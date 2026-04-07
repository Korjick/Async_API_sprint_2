from dataclasses import dataclass
from typing import Protocol

from content_api.internal.core.domain.models.film import SortBy, Film
from content_api.internal.pkg.pagination import PaginatedResult, Pagination
from content_api.internal.ports.input.films.get_films_by_search_handler import \
    FilmsBySearchHandlerProtocol, GetFilmsBySearch
from content_api.internal.ports.output.films_repository import FilmRepository, \
    FilmQueryParams


class GetFilmsBySearchUseCase(FilmsBySearchHandlerProtocol):
    def __init__(self, film_repository: FilmRepository) -> None:
        self.films_repository = film_repository

    async def handle(self, query: GetFilmsBySearch) -> PaginatedResult[Film]:
        query_params = FilmQueryParams(sort=query.sort,
                                       query=query.search_query,
                                       page=query.page,
                                       per_page=query.per_page)
        response = await self.films_repository.search_by_query(query_params)
        return response
