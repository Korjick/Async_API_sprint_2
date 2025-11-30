import logging.config
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

import internal.ports.input.films.get_film_by_id_handler \
    as film_by_id_handler
import internal.ports.input.films.get_films_by_params_handler \
    as films_by_params_handler
import internal.ports.input.films.get_films_by_search_handler \
    as films_by_search_handler
import internal.ports.input.genres.get_all_genres_handler \
    as all_genres_handler
import internal.ports.input.genres.get_genre_by_id_handler \
    as genre_by_id_handler
import internal.ports.input.persons.get_all_persons_handler \
    as all_persons_handler
import internal.ports.input.persons.get_person_by_id_handler \
    as person_by_id_handler
import internal.ports.input.persons.get_persons_by_search_handler \
    as persons_by_search_handler
import internal.ports.output.films_repository as films_repository
import internal.ports.output.genres_repository as genres_repository
import internal.ports.output.persons_repository as persons_repository
import internal.ports.output.cache as cache
from internal.adapters.input.http import base_exception_handlers
from internal.adapters.output.elasticsearch.film.repository import (
    ElasticFilmRepository,
)
from internal.adapters.output.elasticsearch.genre.repository import (
    ElasticGenreRepository,
)
from internal.adapters.output.elasticsearch.person.repository import (
    ElasticPersonRepository,
)
from internal.adapters.output.redis.cache import RedisCache
from internal.core.application.usecases.queries.films.get_film_by_id_query import (
    GetFilmsByIdUseCase,
)
from internal.core.application.usecases.queries.films.get_films_by_params_query import (
    GetFilmsByParamsUseCase,
)
from internal.core.application.usecases.queries.films.get_films_by_search_query import (
    GetFilmsBySearchUseCase,
)
from internal.core.application.usecases.queries.genres.get_all_genres_query import (
    GetAllGenresUseCase,
)
from internal.core.application.usecases.queries.genres.get_genre_by_id_query import (
    GetGenreByIdUseCase,
)
from internal.core.application.usecases.queries.persons.get_all_persons_query import (
    GetAllPersonUseCase,
)
from internal.core.application.usecases.queries.persons.get_person_by_id_query import (
    GetPersonByIdUseCase,
)
from internal.core.application.usecases.queries.persons.get_persons_by_search_query import (
    GetPersonsBySearchUseCase,
)
from internal.infrastructure.app_config import Settings
from internal.infrastructure.logger_config import LOGGING
from internal.adapters.input.http.v1.films import routes as films_routes
from internal.adapters.input.http.v1.genres import routes as genres_routes
from internal.adapters.input.http.v1.persons import routes as persons_routes


def create_app(settings: Settings = Settings()) -> FastAPI:
    logging.config.dictConfig(LOGGING)

    redis_client = Redis(host=settings.redis_host,
                         port=settings.redis_port)
    es_client = AsyncElasticsearch(
        hosts=[
            f"{settings.elastic_schema}"
            f"{settings.elastic_host}:"
            f"{settings.elastic_port}"
        ]
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logging.info("Application started")
        try:
            yield
        finally:
            await redis_client.close()
            await es_client.close()
            logging.info("Application shutdown")

    # Repositories
    films_repository.instance = ElasticFilmRepository(es_client)
    genres_repository.instance = ElasticGenreRepository(es_client)
    persons_repository.instance = ElasticPersonRepository(es_client)

    cache.instance = RedisCache(redis_client, settings.project_name)

    # Use Cases
    film_by_id_handler.instance = GetFilmsByIdUseCase(
        films_repository.instance)
    films_by_params_handler.instance = GetFilmsByParamsUseCase(
        films_repository.instance)
    films_by_search_handler.instance = GetFilmsBySearchUseCase(
        films_repository.instance)

    all_genres_handler.instance = GetAllGenresUseCase(
        genres_repository.instance)
    genre_by_id_handler.instance = GetGenreByIdUseCase(
        genres_repository.instance)

    all_persons_handler.instance = GetAllPersonUseCase(
        persons_repository.instance)
    person_by_id_handler.instance = GetPersonByIdUseCase(
        persons_repository.instance)
    persons_by_search_handler.instance = GetPersonsBySearchUseCase(
        persons_repository.instance)

    app = FastAPI(
        title=settings.project_name,
        docs_url="/api/openapi",
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
        description="Сервис для работы с фильмами, жанрами и актерами",
        lifespan=lifespan,
    )

    base_exception_handlers.setup_exception_handlers(app)

    app.include_router(films_routes.router, prefix="/api/v1")
    app.include_router(genres_routes.router, prefix="/api/v1")
    app.include_router(persons_routes.router, prefix="/api/v1")

    return app


app = create_app()
