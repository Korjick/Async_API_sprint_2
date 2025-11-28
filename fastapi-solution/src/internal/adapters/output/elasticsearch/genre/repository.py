import uuid
from typing import Optional, List

from elasticsearch import AsyncElasticsearch

from internal.adapters.output.elasticsearch.base_repository import ElasticBaseRepository
from internal.core.domain.models.genre import Genre
from internal.ports.output.genres_repository import GenreRepository


class ElasticGenreRepository(ElasticBaseRepository[Genre], GenreRepository):
    def __init__(self, elastic: AsyncElasticsearch):
        super().__init__(elastic, 'genres', Genre)

    async def get_genre_by_id(self, genre_id: uuid.UUID) -> Optional[Genre]:
        return await self.get_by_id(genre_id)

    async def get_all_genres(self) -> List[Genre]:
        return await self.get_list()
