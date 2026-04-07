import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Depends
from content_api.internal.adapters.input.http.dependencies import optional_auth_identity
from content_api.internal.adapters.input.http.v1.films.schemas import FilmShortResponse, \
    FilmDetailResponse, FilmListResponse, FilmSearchByQueryRequest, \
    FilmSearchByParamsRequest
from content_api.internal.ports.input.films.get_film_by_id_handler import \
    FilmByIdHandlerProtocol, get_instance as film_by_id_handler, GetFilmById
from content_api.internal.ports.input.films.get_films_by_params_handler import \
    get_instance as films_by_params_handler, FilmsByParamsHandlerProtocol, \
    GetFilmsByParams
from content_api.internal.ports.input.films.get_films_by_search_handler import \
    FilmsBySearchHandlerProtocol, get_instance as films_by_search_handler, \
    GetFilmsBySearch
from content_api.internal.ports.output.auth_verifier import AuthUserIdentity
from content_api.internal.ports.output.cache import cache_decorator

CACHE_EXPIRE_IN_SECONDS = 60 * 5
router = APIRouter(prefix='/films', tags=['Фильмы'])


@router.get("/search",
            response_model=FilmListResponse,
            summary="Вывод списка кинопроизведений с поиском по названию и описанию и сортировкой")
@cache_decorator(
    expire_sec=CACHE_EXPIRE_IN_SECONDS,
    response_model=FilmListResponse
)
async def films_search(
        search_params: Annotated[FilmSearchByQueryRequest, Depends()],
        films_by_search: Annotated[
            FilmsBySearchHandlerProtocol, Depends(
                films_by_search_handler)],
        auth_user: Annotated[
            Optional[AuthUserIdentity], Depends(
                optional_auth_identity)]) -> FilmListResponse:
    params = GetFilmsBySearch(page=search_params.page,
                              per_page=search_params.per_page,
                              sort=search_params.sort,
                              search_query=search_params.query)
    result = await films_by_search.handle(params)
    return FilmListResponse(
        page=result.page,
        per_page=result.per_page,
        total=result.total,
        items=[FilmShortResponse.from_domain(film) for film in result.items],
    )


@router.get("/{film_id}",
            response_model=FilmDetailResponse,
            summary="Поиск кинопроизведения по id")
@cache_decorator(
    expire_sec=CACHE_EXPIRE_IN_SECONDS,
    response_model=FilmDetailResponse
)
async def film_details(
        film_id: uuid.UUID,
        films_by_id: Annotated[
            FilmByIdHandlerProtocol, Depends(film_by_id_handler)],
        auth_user: Annotated[
            Optional[AuthUserIdentity], Depends(optional_auth_identity)]) \
        -> FilmDetailResponse:
    film = await films_by_id.handle(GetFilmById(id=film_id))
    detail = FilmDetailResponse.from_domain(film)
    return detail


@router.get("/",
            response_model=FilmListResponse,
            summary="Вывод списка кинопроизведений с фильтрацией по жанрам и сортировкой")
@cache_decorator(
    expire_sec=CACHE_EXPIRE_IN_SECONDS,
    response_model=FilmListResponse
)
async def films_list(
        search_params: Annotated[FilmSearchByParamsRequest, Depends()],
        films_by_params: Annotated[
            FilmsByParamsHandlerProtocol, Depends(films_by_params_handler)],
        auth_user: Annotated[
            Optional[AuthUserIdentity], Depends(optional_auth_identity)]) \
        -> FilmListResponse:
    params = GetFilmsByParams(page=search_params.page,
                              per_page=search_params.per_page,
                              sort=search_params.sort,
                              genre=search_params.genre,
                              person=search_params.person)
    result = await films_by_params.handle(params)
    return FilmListResponse(
        page=result.page,
        per_page=result.per_page,
        total=result.total,
        items=[FilmShortResponse.from_domain(film) for film in result.items],
    )
