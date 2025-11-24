import uuid
from dataclasses import dataclass
from typing import Protocol, Optional

from internal.core.domain.models.genre import Genre
from internal.ports.genres_repository import GenreRepository


@dataclass(kw_only=True)
class GetGenreById:
    id: uuid.UUID


class GetGenreByIdHandlerProtocol(Protocol):
    async def handle(self, query: GetGenreById) -> Optional[Genre]:
        pass


class GetGenreByIdHandler:
    def __init__(self, genre_repository: GenreRepository):
        self.genre_repository = genre_repository

    async def handle(self, query: GetGenreById) -> Optional[Genre]:
        return await self.genre_repository.get_genre_by_id(query.id)
