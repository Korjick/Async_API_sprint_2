import uuid
from dataclasses import dataclass
from typing import Protocol

from internal.core.domain.models.film import Film
from internal.ports.films_repository import FilmRepository


@dataclass(kw_only=True)
class GetFilmById:
    id: uuid.UUID


class GetFilmByIdHandlerProtocol(Protocol):
    async def handle(self, query: GetFilmById) \
            -> Film:
        pass


class GetFilmsByIdHandler:
    def __init__(self, film_repository: FilmRepository) -> None:
        self.films_repository = film_repository

    async def handle(self, query: GetFilmById) \
            -> Film:
        response = await self.films_repository.get_film_by_id(query.id)
        return response
