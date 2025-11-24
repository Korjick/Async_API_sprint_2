import logging.config
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from internal.adapters.input.http.v1.films.routes import FilmHandler
from internal.adapters.input.http.v1.genres.routes import GenreHandler
from internal.adapters.input.http.v1.persons.routes import PersonHandler
from internal.adapters.output.elasticsearch.film.repository import (
    ElasticFilmRepository,
)
from internal.adapters.output.elasticsearch.genre.repository import (
    ElasticGenreRepository,
)
from internal.adapters.output.elasticsearch.person.repository import (
    ElasticPersonRepository,
)
from internal.core.application.usecases.queries.films.get_film_by_id_query import (
    GetFilmsByIdHandler,
)
from internal.core.application.usecases.queries.films.get_films_by_params_query import (
    GetFilmsByParamsHandler,
)
from internal.core.application.usecases.queries.films.get_films_by_search_query import (
    GetFilmsBySearchHandler,
)
from internal.core.application.usecases.queries.genres.get_all_genres_query import (
    GetAllGenresHandler,
)
from internal.core.application.usecases.queries.genres.get_genre_by_id_query import (
    GetGenreByIdHandler,
)
from internal.core.application.usecases.queries.persons.get_person_by_id_query import (
    GetPersonByIdHandler,
)
from internal.core.application.usecases.queries.persons.search_persons_query import (
    SearchPersonsHandler,
)
from internal.infrastructure.config import Settings
from internal.infrastructure.exception_handlers import setup_exception_handlers
from internal.infrastructure.logger import LOGGING

logging.config.dictConfig(LOGGING)


def create_app(settings: Settings = Settings()) -> FastAPI:
    redis_client = Redis(host=settings.redis_host, port=settings.redis_port)
    es_client = AsyncElasticsearch(
        hosts=[
            f"{settings.elastic_schema}{settings.elastic_host}:{settings.elastic_port}"
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
    film_repository = ElasticFilmRepository(es_client)
    genre_repository = ElasticGenreRepository(es_client)
    person_repository = ElasticPersonRepository(es_client)

    # Use Cases
    get_film_by_id_uc = GetFilmsByIdHandler(film_repository)
    get_films_by_params_uc = GetFilmsByParamsHandler(film_repository)
    get_films_by_search_uc = GetFilmsBySearchHandler(film_repository)

    get_all_genres_uc = GetAllGenresHandler(genre_repository)
    get_genre_by_id_uc = GetGenreByIdHandler(genre_repository)

    get_person_by_id_uc = GetPersonByIdHandler(person_repository)
    search_persons_uc = SearchPersonsHandler(person_repository)

    # Handlers
    film_handler = FilmHandler(
        app_title=settings.project_name,
        get_film_by_search=get_films_by_search_uc,
        get_film_by_params=get_films_by_params_uc,
        get_film_by_id=get_film_by_id_uc,
        redis=redis_client,
    )

    genre_handler = GenreHandler(
        get_all_genres=get_all_genres_uc,
        get_genre_by_id=get_genre_by_id_uc,
    )

    person_handler = PersonHandler(
        get_person_by_id=get_person_by_id_uc,
        search_persons=search_persons_uc,
        get_films_by_params=get_films_by_params_uc,
    )

    app = FastAPI(
        title=settings.project_name,
        docs_url="/api/openapi",
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
        description="Сервис для работы с фильмами, жанрами и актерами",
        lifespan=lifespan,
    )

    setup_exception_handlers(app)

    app.include_router(film_handler.router, prefix="/api/v1")
    app.include_router(genre_handler.router, prefix="/api/v1")
    app.include_router(person_handler.router, prefix="/api/v1")

    return app


app = create_app()
