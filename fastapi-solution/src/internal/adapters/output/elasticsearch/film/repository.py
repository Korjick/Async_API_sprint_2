import uuid
from uuid import UUID

from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch, NotFoundError

from internal.adapters.output.elasticsearch.base_repository import (
    ElasticBaseRepository,
)
from internal.adapters.output.elasticsearch.utils import es_sort
from internal.core.domain.models.film import Film
from internal.core.domain.models.genre import Genre
from internal.core.domain.models.person import Person
from internal.pkg.errors import ObjectNotFoundError
from internal.pkg.pagination import PaginatedResult
from internal.ports.films_repository import (
    FilmSearchParams,
    FilmQueryParams,
    FilmRepository,
)


class ElasticFilmRepository(ElasticBaseRepository[Film], FilmRepository):
    def __init__(self, elastic: AsyncElasticsearch):
        super().__init__(elastic, 'movies', Film)

    async def search_by_params(self, search_params: FilmSearchParams) \
            -> PaginatedResult[Film]:
        """Поиск фильмов по параметрам (жанр, персона)."""
        must_clauses = []

        if search_params.genre:
            must_clauses.append({
                "nested": {
                    "path": "genres",
                    "query": {
                        "term": {
                            "genres.id": search_params.genre
                        }
                    }
                }
            })

        if search_params.person:
            # Индекс создаётся без nested-мэппинга, поэтому фильтруем по полям
            # actors.id / writers.id / directors.id без nested-запросов.
            person_id = str(search_params.person)
            must_clauses.append(
                {
                    "bool": {
                        "should": [
                            {"term": {"actors.id": person_id}},
                            {"term": {"writers.id": person_id}},
                            {"term": {"directors.id": person_id}},
                        ],
                        "minimum_should_match": 1,
                    }
                }
            )

        if must_clauses:
            query = {
                "bool": {
                    "must": must_clauses
                }
            }
        else:
            query = {"match_all": {}}

        body = {
            "sort": es_sort(search_params.sort.value),
            "query": query,
            "from": (search_params.page - 1) * search_params.per_page,
            "size": search_params.per_page,
            "track_total_hits": True,
            "_source": ["id", "title", "imdb_rating"],
        }

        try:
            res = await self.elastic.search(index=self.index_name, body=body)
        except NotFoundError:
            raise ObjectNotFoundError(param_name="index", entity_id=self.index_name)

        # Если фильтрация по person ничего не дала, пробуем найти фильмы по имени
        # персоны через индексы directors_names / writers_names / actors_names.
        if search_params.person and res["hits"]["total"]["value"] == 0:
            person_id = str(search_params.person)
            try:
                person_doc = await self.elastic.get(index="persons", id=person_id)
            except NotFoundError:
                raise ObjectNotFoundError(param_name="id", entity_id=search_params.person)
            else:
                person_name = person_doc["_source"]["full_name"]
                fallback_body = {
                    "query": {
                        "multi_match": {
                            "query": person_name,
                            "fields": [
                                "directors_names",
                                "writers_names",
                                "actors_names",
                            ],
                            "type": "phrase",
                        }
                    },
                    "sort": es_sort(search_params.sort.value),
                    "from": (search_params.page - 1) * search_params.per_page,
                    "size": search_params.per_page,
                    "track_total_hits": True,
                    # здесь не ограничиваем _source, чтобы получить актёров/режиссёров
                }
                try:
                    res = await self.elastic.search(index=self.index_name, body=fallback_body)
                except NotFoundError:
                    raise ObjectNotFoundError(param_name="index", entity_id=self.index_name)

        return self._es_result_as_paginated_result(
            res,
            search_params.page,
            search_params.per_page,
        )

    async def search_by_query(self, query_params: FilmQueryParams) \
            -> PaginatedResult[Film]:
        """Поиск фильмов по текстовому запросу."""
        if not query_params.query:
            query = {"match_all": {}}
        else:
            query = {
                "multi_match": {
                    "query": query_params.query,
                    "type": "cross_fields",
                    "fields": [
                        "title^3",
                        "description^1",
                    ],
                    "operator": "and",
                    "minimum_should_match": "75%",
                }
            }

        body = {
            "query": query,
            "sort": es_sort(query_params.sort.value),
            "from": (query_params.page - 1) * query_params.per_page,
            "size": query_params.per_page,
            "track_total_hits": True,
            "_source": ["id", "title", "imdb_rating"],
        }

        try:
            res = await self.elastic.search(index=self.index_name, body=body)
        except NotFoundError:
            raise ObjectNotFoundError(param_name="index", entity_id=self.index_name)

        return self._es_result_as_paginated_result(
            res,
            query_params.page,
            query_params.per_page,
        )

    async def get_film_by_id(self, film_id: UUID) -> Film:
        """Получить фильм по ID с маппингом вложенных сущностей."""
        try:
            res = await self.elastic.get(index=self.index_name, id=str(film_id))
        except NotFoundError:
            raise ObjectNotFoundError(param_name="id", entity_id=film_id)

        source = res["_source"]

        genres = [Genre(name=g) for g in source.get("genres", [])]
        actors = [
            Person(oid=uuid.UUID(p["id"]), full_name=p["name"])
            for p in source.get("actors", [])
        ]
        writers = [
            Person(oid=uuid.UUID(p["id"]), full_name=p["name"])
            for p in source.get("writers", [])
        ]
        directors = [
            Person(oid=uuid.UUID(p["id"]), full_name=p["name"])
            for p in source.get("directors", [])
        ]

        return Film(
            title=source["title"],
            oid=uuid.UUID(res["_id"]),
            description=source.get("description"),
            imdb_rating=source.get("imdb_rating"),
            genres=genres,
            actors=actors,
            writers=writers,
            directors=directors,
        )

    @classmethod
    def _es_result_as_paginated_result(
            cls,
            res: ObjectApiResponse,
            page: int,
            size: int,
    ) -> PaginatedResult[Film]:
        items: list[Film] = []
        for hit in res["hits"]["hits"]:
            source = hit["_source"]

            genres = [
                Genre(name=g["name"], oid=uuid.UUID(g["id"]))
                for g in source.get("genres", [])
            ]
            actors = [
                Person(oid=uuid.UUID(p["id"]), full_name=p["name"])
                for p in source.get("actors", [])
            ]
            writers = [
                Person(oid=uuid.UUID(p["id"]), full_name=p["name"])
                for p in source.get("writers", [])
            ]
            directors = [
                Person(oid=uuid.UUID(p["id"]), full_name=p["name"])
                for p in source.get("directors", [])
            ]

            film = Film(
                title=source["title"],
                oid=uuid.UUID(hit["_id"]),
                description=source.get("description"),
                imdb_rating=source.get("imdb_rating"),
                genres=genres,
                actors=actors,
                writers=writers,
                directors=directors,
            )
            items.append(film)

        total_hits = res["hits"]["total"]
        if isinstance(total_hits, dict):
            total_hits = total_hits.get("value", 0)

        return PaginatedResult[Film](
            items=items,
            page=page,
            per_page=size,
            total=total_hits,
        )
