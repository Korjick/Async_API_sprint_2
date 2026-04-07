from content_api.internal.core.domain.models.film import Film
from content_api.internal.ports.input.films.get_film_by_id_handler import GetFilmById, \
    FilmByIdHandlerProtocol
from content_api.internal.ports.output.films_repository import FilmRepository


class GetFilmsByIdUseCase(FilmByIdHandlerProtocol):
    def __init__(self, film_repository: FilmRepository) -> None:
        self.films_repository = film_repository

    async def handle(self, query: GetFilmById) -> Film:
        response = await self.films_repository.get_film_by_id(query.id)
        return response
