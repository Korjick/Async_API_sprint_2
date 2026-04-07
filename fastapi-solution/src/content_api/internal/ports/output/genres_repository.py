import uuid
from typing import Protocol, Optional, List

from content_api.internal.core.domain.models.genre import Genre


class GenreRepository(Protocol):
    async def get_genre_by_id(self, genre_id: uuid.UUID) -> Optional[Genre]:
        pass

    async def get_all_genres(self) -> List[Genre]:
        pass


instance: Optional[GenreRepository] = None


def get_instance() -> GenreRepository:
    if instance is None:
        raise RuntimeError("Genre repository is not initialized")
    return instance
