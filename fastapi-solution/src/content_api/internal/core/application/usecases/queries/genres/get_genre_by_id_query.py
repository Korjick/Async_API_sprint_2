from content_api.internal.core.domain.models.genre import Genre
from content_api.internal.ports.input.genres.get_genre_by_id_handler import \
    GenreByIdHandlerProtocol, GetGenreById
from content_api.internal.ports.output.genres_repository import GenreRepository


class GetGenreByIdUseCase(GenreByIdHandlerProtocol):
    def __init__(self, genre_repository: GenreRepository):
        self.genre_repository = genre_repository

    async def handle(self, query: GetGenreById) -> Genre:
        return await self.genre_repository.get_genre_by_id(query.id)
