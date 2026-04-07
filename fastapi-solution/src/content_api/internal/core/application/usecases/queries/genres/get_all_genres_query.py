from typing import List

from content_api.internal.core.domain.models.genre import Genre
from content_api.internal.ports.input.genres.get_all_genres_handler import \
    AllGenresHandlerProtocol, GetAllGenres
from content_api.internal.ports.output.genres_repository import GenreRepository


class GetAllGenresUseCase(AllGenresHandlerProtocol):
    def __init__(self, genre_repository: GenreRepository):
        self.genre_repository = genre_repository

    async def handle(self, query: GetAllGenres) -> List[Genre]:
        return await self.genre_repository.get_all_genres()
