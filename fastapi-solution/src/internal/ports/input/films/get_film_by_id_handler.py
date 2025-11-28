import uuid
from dataclasses import dataclass
from typing import Protocol, Optional

from internal.core.domain.models.film import Film


@dataclass(kw_only=True)
class GetFilmById:
    id: uuid.UUID


class FilmByIdHandlerProtocol(Protocol):
    async def handle(self, query: GetFilmById) -> Film:
        pass


instance: Optional[FilmByIdHandlerProtocol] = None


def get_instance() -> FilmByIdHandlerProtocol:
    if instance is None:
        raise RuntimeError("Film by id handler is not initialized")
    return instance
