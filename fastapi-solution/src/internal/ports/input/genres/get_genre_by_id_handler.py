import uuid
from dataclasses import dataclass
from typing import Protocol, Optional

from internal.core.domain.models.genre import Genre


@dataclass(kw_only=True)
class GetGenreById:
    id: uuid.UUID


class GenreByIdHandlerProtocol(Protocol):
    async def handle(self, query: GetGenreById) -> Genre:
        pass


instance: Optional[GenreByIdHandlerProtocol] = None


def get_instance() -> GenreByIdHandlerProtocol:
    if instance is None:
        raise RuntimeError("Genre by id handler is not initialized")
    return instance
