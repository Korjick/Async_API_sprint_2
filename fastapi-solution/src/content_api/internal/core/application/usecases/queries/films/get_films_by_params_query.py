from content_api.internal.core.domain.models.film import Film
from content_api.internal.pkg.pagination import PaginatedResult
from content_api.internal.ports.input.films.get_films_by_params_handler import \
    FilmsByParamsHandlerProtocol, GetFilmsByParams
from content_api.internal.ports.output.films_repository import FilmRepository, \
    FilmSearchParams


class GetFilmsByParamsUseCase(FilmsByParamsHandlerProtocol):
    def __init__(self, film_repository: FilmRepository) -> None:
        self.films_repository = film_repository

    async def handle(self, query: GetFilmsByParams) -> PaginatedResult[Film]:
        search_params = FilmSearchParams(sort=query.sort,
                                         genre=query.genre,
                                         person=query.person,
                                         page=query.page,
                                         per_page=query.per_page)
        response = await self.films_repository.search_by_params(search_params)
        return response
