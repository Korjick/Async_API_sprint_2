import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis

from internal.adapters.input.http.v1.films.schemas import FilmShortResponse, \
    FilmDetailResponse, FilmListResponse, FilmSearchByQueryRequest, \
    FilmSearchByParamsRequest
from internal.infrastructure.redis import \
    cache_response as redis_cache_response
from internal.core.application.usecases.queries.films.get_film_by_id_query import \
    GetFilmById, GetFilmByIdHandlerProtocol
from internal.core.application.usecases.queries.films.get_films_by_params_query import \
    GetFilmsByParams, GetFilmsByParamsHandlerProtocol
from internal.core.application.usecases.queries.films.get_films_by_search_query import \
    GetFilmsBySearch, GetFilmsBySearchHandlerProtocol

CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmHandler:
    def __init__(self,
                 app_title: str,
                 get_film_by_search: GetFilmsBySearchHandlerProtocol,
                 get_film_by_id: GetFilmByIdHandlerProtocol,
                 get_film_by_params: GetFilmsByParamsHandlerProtocol,
                 redis: Redis) -> None:
        self.app_title = app_title
        self.redis = redis
        self.get_film_by_search = get_film_by_search
        self.get_film_by_id = get_film_by_id
        self.get_film_by_params = get_film_by_params

        self.router = APIRouter(prefix='/films', tags=['Фильмы'])
        self.router.add_api_route('/search',
                                  endpoint=self.films_search,
                                  methods=["GET"],
                                  response_model=FilmListResponse,
                                  summary="Вывод списка кинопроизведений с поиском по названию и описанию и сортировкой")
        self.router.add_api_route('/{film_id}',
                                  endpoint=self.film_details,
                                  methods=["GET"],
                                  response_model=FilmDetailResponse,
                                  summary="Поиск кинопроизведения по id"
                                  )
        self.router.add_api_route('/',
                                  endpoint=self.films_list,
                                  methods=["GET"],
                                  response_model=FilmListResponse,
                                  summary="Вывод списка кинопроизведений с фильтрацией по жанрам и сортировкой")

    @redis_cache_response(
        expire_sec=CACHE_EXPIRE_IN_SECONDS,
        response_model=FilmListResponse
    )
    async def films_search(self,
                           search_params: Annotated[
                               FilmSearchByQueryRequest, Depends()]) \
            -> FilmListResponse:
        params = GetFilmsBySearch(page=search_params.page,
                                  per_page=search_params.per_page,
                                  sort=search_params.sort,
                                  search_query=search_params.query)
        result = await self.get_film_by_search.handle(params)

        return FilmListResponse(
            page=result.page,
            per_page=result.per_page,
            total=result.total,
            items=[FilmShortResponse.from_domain(film) for film in result.items],
        )

    @redis_cache_response(
        expire_sec=CACHE_EXPIRE_IN_SECONDS,
        response_model=FilmDetailResponse
    )
    async def film_details(self, film_id: uuid.UUID) -> FilmDetailResponse:
        film = await self.get_film_by_id.handle(GetFilmById(id=film_id))
        detail = FilmDetailResponse.from_domain(film)
        print("film_details: film.genres=", film.genres, "detail.genres=", detail.genres)
        return detail

    @redis_cache_response(
        expire_sec=CACHE_EXPIRE_IN_SECONDS,
        response_model=FilmListResponse
    )
    async def films_list(self,
                         search_params: Annotated[
                             FilmSearchByParamsRequest, Depends()]) \
            -> FilmListResponse:
        params = GetFilmsByParams(page=search_params.page,
                                  per_page=search_params.per_page,
                                  sort=search_params.sort,
                                  genre=search_params.genre,
                                  person=search_params.person)
        result = await self.get_film_by_params.handle(params)

        return FilmListResponse(
            page=result.page,
            per_page=result.per_page,
            total=result.total,
            items=[FilmShortResponse.from_domain(film) for film in result.items],
        )
