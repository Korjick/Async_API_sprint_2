import uuid
from typing import List

from elasticsearch import AsyncElasticsearch

from internal.adapters.output.elasticsearch.base_repository import \
    ElasticBaseRepository
from internal.core.domain.models.film import Film
from internal.core.domain.models.person import Person
from internal.pkg.pagination import PaginatedResult
from internal.ports.output.persons_repository import PersonRepository


class ElasticPersonRepository(ElasticBaseRepository[Person], PersonRepository):
    def __init__(self, elastic: AsyncElasticsearch):
        super().__init__(elastic, 'persons', Person)

    async def get_person_by_id(self, person_id: uuid.UUID) -> Person:
        return await self.get_by_id(person_id)

    async def get_all_persons(self) -> List[Person]:
        return await self.get_list()

    async def get_films_by_person(self, person: Person) -> List[Film]:
        query = {
            "multi_match": {
                "query": person.full_name,
                "fields": ["directors_names", "writers_names", "actors_names"],
                "type": "phrase"
            }
        }
        body = {
            "query": query
        }
        response = await self.elastic.search(
            index='movies',
            body=body
        )

        films = [Film(**hit["_source"]) for hit in response["hits"]["hits"]]
        return films

    async def search_by_name(self, query: str, page: int, per_page: int) \
            -> PaginatedResult[Person]:
        body = {
            "query": {
                "match": {
                    "full_name": {
                        "query": query,
                        "fuzziness": "auto"
                    }
                }
            },
            "from": (page - 1) * per_page,
            "size": per_page
        }

        response = await self.elastic.search(index=self.index_name, body=body)
        items = [Person(oid=uuid.UUID(hit["_id"]),
                        full_name=hit["_source"]["full_name"])
                 for hit in response["hits"]["hits"]]

        total = response["hits"]["total"]["value"]

        return PaginatedResult(
            items=items,
            total=total,
            page=page,
            per_page=per_page
        )
