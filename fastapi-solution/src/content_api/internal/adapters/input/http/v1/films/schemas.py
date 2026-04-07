from typing import List, Optional, Union

from pydantic import BaseModel, Field, ConfigDict

from content_api.internal.adapters.input.http.base_schemas import PaginatedResponse, \
    PaginationRequest
from content_api.internal.adapters.input.http.v1.persons.schemas import Person
from content_api.internal.core.domain.models.film import SortBy, Film


class FilmPersonResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    uuid: str = Field(alias="id")
    full_name: str

    @classmethod
    def from_domain(cls, person: Person):
        return cls(id=str(person.id), full_name=person.full_name)


class FilmShortResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    uuid: str = Field(alias="id")
    title: str
    imdb_rating: Optional[float] = None

    @classmethod
    def from_domain(cls, film: Film):
        return cls(id=str(film.id),
                   title=film.title,
                   imdb_rating=film.imdb_rating)


class FilmDetailResponse(FilmShortResponse):
    description: Optional[str] = None
    # Допускаем как строки, так и словари (id/name),
    # чтобы не падать при различных форматах источника.
    genres: List[Union[str, dict]] = Field(default_factory=list)
    actors: List[FilmPersonResponse] = Field(default_factory=list)
    writers: List[FilmPersonResponse] = Field(default_factory=list)
    directors: List[FilmPersonResponse] = Field(default_factory=list)

    @classmethod
    def from_domain(cls, film: Film):
        return cls(id=str(film.id),
                   title=film.title,
                   imdb_rating=film.imdb_rating,
                   description=film.description,
                   genres=list(map(lambda genre: genre.name, film.genres)),
                   actors=[FilmPersonResponse.from_domain(p) for p in film.actors],
                   writers=[FilmPersonResponse.from_domain(p) for p in film.writers],
                   directors=[FilmPersonResponse.from_domain(p) for p in
                              film.directors])


class FilmListResponse(PaginatedResponse[FilmShortResponse]):
    ...


class FilmSearchByQueryRequest(PaginationRequest):
    sort: Optional[SortBy] = Field(SortBy.IMDB_RATING_DESC,
                                   description="Поле для сортировки")
    query: Optional[str] = Field(None, description="Поисковый запрос")


class FilmSearchByParamsRequest(PaginationRequest):
    sort: Optional[SortBy] = Field(SortBy.IMDB_RATING_DESC,
                                   description="Поле для сортировки")
    genre: Optional[str] = Field(None, description="UUID жанра")
    person: Optional[str] = Field(None, description="UUID персоны")
