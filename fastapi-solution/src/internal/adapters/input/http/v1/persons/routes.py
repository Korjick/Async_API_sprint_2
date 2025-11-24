import uuid
from typing import List, Annotated

from fastapi import APIRouter, Query
from fastapi.params import Depends

from internal.adapters.input.http.base import PaginationRequest
from internal.adapters.input.http.v1.films.schemas import FilmShortResponse
from internal.adapters.input.http.v1.persons.schemas import (
    PersonDetailResponse,
    PersonFilmResponse,
    PersonListResponse,
)
from internal.core.application.usecases.queries.films.get_films_by_params_query import (
    GetFilmsByParamsHandlerProtocol,
    GetFilmsByParams,
)
from internal.core.application.usecases.queries.persons.get_person_by_id_query import (
    GetPersonByIdHandlerProtocol,
    GetPersonById,
)
from internal.core.application.usecases.queries.persons.search_persons_query import (
    SearchPersonsHandlerProtocol,
    SearchPersons,
)
from internal.core.domain.models.film import Film, SortBy


class PersonHandler:
    def __init__(
            self,
            get_person_by_id: GetPersonByIdHandlerProtocol,
            search_persons: SearchPersonsHandlerProtocol,
            get_films_by_params: GetFilmsByParamsHandlerProtocol,
    ):
        self.get_person_by_id = get_person_by_id
        self.search_persons = search_persons
        self.get_films_by_params = get_films_by_params

        self.router = APIRouter(prefix='/persons', tags=['Персоны'])

        self.router.add_api_route(
            '/search',
            self.person_search,
            methods=["GET"],
            response_model=PersonListResponse,
            summary="Поиск персон по имени",
        )
        self.router.add_api_route(
            '/{person_id}',
            self.person_details,
            methods=["GET"],
            response_model=PersonDetailResponse,
            summary="Получить персону по id",
        )
        self.router.add_api_route(
            '/{person_id}/film',
            self.person_films,
            methods=["GET"],
            response_model=List[FilmShortResponse],
            summary="Получить фильмы по id персоны",
        )

    async def person_search(
            self,
            pagination: Annotated[PaginationRequest, Depends()],
            query: str = Query(..., min_length=1),
    ) -> PersonListResponse:
        search_query = SearchPersons(
            query=query,
            page=pagination.page,
            per_page=pagination.per_page,
        )
        paginated_persons = await self.search_persons.handle(search_query)

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
            films_result = await self.get_films_by_params.handle(films_query)

            films_response: List[PersonFilmResponse] = []
            for film in films_result.items:
                roles = self._get_roles(person.id, film)
                films_response.append(
                    PersonFilmResponse(
                        uuid=str(film.id),
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

    async def person_details(
            self,
            person_id: uuid.UUID,
            pagination: Annotated[PaginationRequest, Depends()],
    ) -> PersonDetailResponse:
        """Получить персону и её фильмы по id"""
        person = await self.get_person_by_id.handle(GetPersonById(id=person_id))

        films_query = GetFilmsByParams(
            person=person.id,
            page=pagination.page,
            per_page=pagination.per_page,
            sort=SortBy.IMDB_RATING_DESC,
        )
        films_result = await self.get_films_by_params.handle(films_query)

        films_response: List[PersonFilmResponse] = []
        for film in films_result.items:
            roles = self._get_roles(person.id, film)
            films_response.append(
                PersonFilmResponse(
                    uuid=str(film.id),
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

    async def person_films(
            self,
            person_id: uuid.UUID,
            pagination: Annotated[PaginationRequest, Depends()],
    ) -> List[FilmShortResponse]:
        """Получить фильмы по id персоны"""
        person = await self.get_person_by_id.handle(GetPersonById(id=person_id))

        films_query = GetFilmsByParams(
            person=person.id,
            page=pagination.page,
            per_page=pagination.per_page,
            sort=SortBy.IMDB_RATING_DESC,
        )
        films_result = await self.get_films_by_params.handle(films_query)

        return [FilmShortResponse.from_domain(film) for film in films_result.items]

    @classmethod
    def _get_roles(cls, person_id: uuid.UUID, film: Film) -> List[str]:
        roles: List[str] = []
        # debug print to understand role mapping
        print("get_roles: person_id", person_id, "film_id", film.id,
              "director_ids", [p.id for p in getattr(film, "directors", [])])
        if any(p.id == person_id for p in film.directors):
            roles.append('director')
        if any(p.id == person_id for p in film.writers):
            roles.append('writer')
        if any(p.id == person_id for p in film.actors):
            roles.append('actor')
        return roles
