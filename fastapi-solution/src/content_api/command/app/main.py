from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

import content_api.internal.infrastructure.auth_client as auth_client
import content_api.internal.ports.input.films.get_film_by_id_handler as film_by_id_handler
import content_api.internal.ports.input.films.get_films_by_params_handler as films_by_params_handler
import content_api.internal.ports.input.films.get_films_by_search_handler as films_by_search_handler
import content_api.internal.ports.input.genres.get_all_genres_handler as all_genres_handler
import content_api.internal.ports.input.genres.get_genre_by_id_handler as genre_by_id_handler
import content_api.internal.ports.input.persons.get_all_persons_handler as all_persons_handler
import content_api.internal.ports.input.persons.get_person_by_id_handler as person_by_id_handler
import content_api.internal.ports.input.persons.get_persons_by_search_handler as persons_by_search_handler
import content_api.internal.ports.output.auth_verifier as auth_verifier
import content_api.internal.ports.output.cache as cache
import content_api.internal.ports.output.films_repository as films_repository
import content_api.internal.ports.output.genres_repository as genres_repository
import content_api.internal.ports.output.persons_repository as persons_repository
from content_api.internal.adapters.input.http import base_exception_handlers
from content_api.internal.adapters.input.http.middlewares.request_middleware import (
    RequestContextMiddleware,
)
from content_api.internal.adapters.input.http.v1.films import routes as films_routes
from content_api.internal.adapters.input.http.v1.genres import routes as genres_routes
from content_api.internal.adapters.input.http.v1.persons import routes as persons_routes
from content_api.internal.adapters.output.elasticsearch.film.repository import (
    ElasticFilmRepository,
)
from content_api.internal.adapters.output.elasticsearch.genre.repository import (
    ElasticGenreRepository,
)
from content_api.internal.adapters.output.elasticsearch.person.repository import (
    ElasticPersonRepository,
)
from content_api.internal.adapters.output.redis.cache import RedisCache
from content_api.internal.core.application.usecases.queries.films.get_film_by_id_query import (
    GetFilmsByIdUseCase,
)
from content_api.internal.core.application.usecases.queries.films.get_films_by_params_query import (
    GetFilmsByParamsUseCase,
)
from content_api.internal.core.application.usecases.queries.films.get_films_by_search_query import (
    GetFilmsBySearchUseCase,
)
from content_api.internal.core.application.usecases.queries.genres.get_all_genres_query import (
    GetAllGenresUseCase,
)
from content_api.internal.core.application.usecases.queries.genres.get_genre_by_id_query import (
    GetGenreByIdUseCase,
)
from content_api.internal.core.application.usecases.queries.persons.get_all_persons_query import (
    GetAllPersonUseCase,
)
from content_api.internal.core.application.usecases.queries.persons.get_person_by_id_query import (
    GetPersonByIdUseCase,
)
from content_api.internal.core.application.usecases.queries.persons.get_persons_by_search_query import (
    GetPersonsBySearchUseCase,
)
from content_api.internal.infrastructure.app_config import Settings
from content_api.internal.infrastructure.logger import StructlogLogger
from content_api.internal.infrastructure.telemetry import (
    setup_telemetry,
    shutdown_telemetry,
)
from content_api.internal.ports.output.logger import Logger


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        settings = Settings()

    StructlogLogger.configure(
        json_logs=settings.log_json,
        log_level=settings.log_level,
    )
    app_logger: Logger = StructlogLogger.from_name(__name__)

    redis_client = Redis(host=settings.redis_host, port=settings.redis_port)
    es_client = AsyncElasticsearch(
        hosts=[
            f"{settings.elastic_schema}"
            f"{settings.elastic_host}:"
            f"{settings.elastic_port}"
        ]
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app_logger.info("application_started")
        try:
            yield
        finally:
            await redis_client.close()
            await es_client.close()
            shutdown_telemetry()
            app_logger.info("application_shutdown")

    # Repositories
    films_repository.instance = ElasticFilmRepository(es_client)
    genres_repository.instance = ElasticGenreRepository(es_client)
    persons_repository.instance = ElasticPersonRepository(es_client)
    cache.instance = RedisCache(redis_client, settings.project_name)
    auth_verifier.instance = auth_client.AuthGrpcClient(
        host=settings.auth_grpc_host,
        port=settings.auth_grpc_port,
        timeout_seconds=settings.auth_grpc_timeout_seconds,
    )

    # Use Cases
    film_by_id_handler.instance = GetFilmsByIdUseCase(films_repository.instance)
    films_by_params_handler.instance = GetFilmsByParamsUseCase(
        films_repository.instance
    )
    films_by_search_handler.instance = GetFilmsBySearchUseCase(
        films_repository.instance
    )
    all_genres_handler.instance = GetAllGenresUseCase(genres_repository.instance)
    genre_by_id_handler.instance = GetGenreByIdUseCase(genres_repository.instance)
    all_persons_handler.instance = GetAllPersonUseCase(persons_repository.instance)
    person_by_id_handler.instance = GetPersonByIdUseCase(persons_repository.instance)
    persons_by_search_handler.instance = GetPersonsBySearchUseCase(
        persons_repository.instance
    )

    app = FastAPI(
        title=settings.project_name,
        docs_url="/api/openapi",
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
        description="Service for films, genres and persons",
        lifespan=lifespan,
    )
    app.state.logger = app_logger
    app.add_middleware(RequestContextMiddleware)
    setup_telemetry(app=app, settings=settings)
    app_logger.info(
        "telemetry_configured",
        otel_endpoint=settings.otel_exporter_otlp_endpoint,
        otel_service_name=settings.otel_service_name,
    )

    base_exception_handlers.setup_exception_handlers(app)
    app.include_router(films_routes.router, prefix="/api/v1")
    app.include_router(genres_routes.router, prefix="/api/v1")
    app.include_router(persons_routes.router, prefix="/api/v1")

    return app


app = create_app()
