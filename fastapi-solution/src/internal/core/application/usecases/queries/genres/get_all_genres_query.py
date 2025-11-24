from dataclasses import dataclass
from typing import Protocol, List

from internal.core.domain.models.genre import Genre
from internal.ports.genres_repository import GenreRepository


@dataclass(kw_only=True)
class GetAllGenres:
    pass


class GetAllGenresHandlerProtocol(Protocol):
    async def handle(self, query: GetAllGenres) -> List[Genre]:
        pass


class GetAllGenresHandler:
    def __init__(self, genre_repository: GenreRepository):
        self.genre_repository = genre_repository

    async def handle(self, query: GetAllGenres) -> List[Genre]:
        return await self.genre_repository.get_all_genres()
