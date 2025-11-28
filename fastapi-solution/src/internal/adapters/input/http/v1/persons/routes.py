import uuid
from typing import List, Annotated

from fastapi import APIRouter, Query
from fastapi.params import Depends

from internal.adapters.input.http.base_schemas import PaginationRequest
from internal.adapters.input.http.v1.films.schemas import FilmShortResponse
from internal.adapters.input.http.v1.persons.schemas import (
    PersonDetailResponse,
    PersonFilmResponse,
    PersonListResponse,
)
from internal.core.domain.models.film import Film, SortBy
from internal.ports.input.films.get_films_by_params_handler import \
    get_instance as films_by_params_handler, FilmsByParamsHandlerProtocol, \
    GetFilmsByParams
from internal.ports.input.persons.get_person_by_id_handler import \
    PersonByIdHandlerProtocol, get_instance as person_by_id_handler, \
    GetPersonById
from internal.ports.input.persons.get_persons_by_search_handler import \
    PersonsBySearchHandlerProtocol, get_instance as persons_by_search_handler, \
    SearchPersons

router = APIRouter(prefix='/persons', tags=['Персоны'])


@router.get("/search",
            response_model=PersonListResponse,
            summary="Поиск персон по имени")
async def person_search(pagination: Annotated[PaginationRequest, Depends()],
                        persons_by_search: Annotated[
                            PersonsBySearchHandlerProtocol, Depends(persons_by_search_handler)],
                        films_by_params: Annotated[
                            FilmsByParamsHandlerProtocol, Depends(films_by_params_handler)],
                        query: str = Query(...,
                                           min_length=1)) -> PersonListResponse:
    search_query = SearchPersons(
        query=query,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    paginated_persons = await persons_by_search.handle(search_query)

    if not paginated_persons.items:
        return PersonListResponse(
            items=[],
            total=0,
            page=pagination.page,
            per_page=pagination.per_page,
        )

    items: List[PersonDetailResponse] = []
    for person in paginated_persons.items:
        films_query = GetFilmsByParams(
            person=person.id,
            page=pagination.page,
            per_page=pagination.per_page,
            sort=SortBy.IMDB_RATING_DESC,
        )
        films_result = await films_by_params.handle(films_query)

        films_response: List[PersonFilmResponse] = []
        for film in films_result.items:
            roles = _get_roles(person.id, film)
            films_response.append(
                PersonFilmResponse(
                    id=str(film.id),
                    title=film.title,
                    imdb_rating=film.imdb_rating,
                    roles=roles,
                )
            )

        items.append(
            PersonDetailResponse(
                id=str(person.id),
                full_name=person.full_name,
                films=films_response,
            )
        )

    return PersonListResponse(
        items=items,
        total=paginated_persons.total,
        page=paginated_persons.page,
        per_page=paginated_persons.per_page,
    )


@router.get("/{person_id}",
            response_model=PersonDetailResponse,
            summary="Получить персону по id")
async def person_details(person_id: uuid.UUID,
                         pagination: Annotated[PaginationRequest, Depends()],
                         person_by_id: Annotated[
                             PersonByIdHandlerProtocol, Depends(person_by_id_handler)],
                         films_by_params: Annotated[
                             FilmsByParamsHandlerProtocol,
                             Depends(films_by_params_handler)]) \
        -> PersonDetailResponse:
    person = await person_by_id.handle(GetPersonById(id=person_id))

    films_query = GetFilmsByParams(
        person=person.id,
        page=pagination.page,
        per_page=pagination.per_page,
        sort=SortBy.IMDB_RATING_DESC,
    )
    films_result = await films_by_params.handle(films_query)

    films_response: List[PersonFilmResponse] = []
    for film in films_result.items:
        roles = _get_roles(person.id, film)
        films_response.append(
            PersonFilmResponse(
                id=str(film.id),
                title=film.title,
                imdb_rating=film.imdb_rating,
                roles=roles,
            )
        )

    return PersonDetailResponse(
        id=str(person.id),
        full_name=person.full_name,
        films=films_response,
    )


@router.get("/{person_id}/film",
            response_model=List[FilmShortResponse],
            summary="Получить фильмы по id персоны")
async def person_films(person_id: uuid.UUID,
                       pagination: Annotated[PaginationRequest, Depends()],
                       person_by_id: Annotated[
                           PersonByIdHandlerProtocol, Depends(person_by_id_handler)],
                       films_by_params: Annotated[
                           FilmsByParamsHandlerProtocol,
                           Depends(films_by_params_handler)]) -> \
List[FilmShortResponse]:
    person = await person_by_id.handle(GetPersonById(id=person_id))

    films_query = GetFilmsByParams(
        person=person.id,
        page=pagination.page,
        per_page=pagination.per_page,
        sort=SortBy.IMDB_RATING_DESC,
    )
    films_result = await films_by_params.handle(films_query)

    return [FilmShortResponse.from_domain(film) for film in films_result.items]


def _get_roles(person_id: uuid.UUID, film: Film) -> List[str]:
    roles: List[str] = []
    if any(p.id == person_id for p in film.directors):
        roles.append('director')
    if any(p.id == person_id for p in film.writers):
        roles.append('writer')
    if any(p.id == person_id for p in film.actors):
        roles.append('actor')
    return roles
