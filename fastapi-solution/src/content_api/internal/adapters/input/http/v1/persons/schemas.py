from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from content_api.internal.adapters.input.http.base_schemas import PaginatedResponse
from content_api.internal.core.domain.models.person import Person


class PersonFilmResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    uuid: str = Field(alias="id")
    title: str
    imdb_rating: Optional[float]
    roles: List[str]


class PersonShortResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    uuid: str = Field(alias="id")
    full_name: str

    @classmethod
    def from_domain(cls, person: Person):
        return cls(id=str(person.id), full_name=person.full_name)


class PersonDetailResponse(PersonShortResponse):
    films: List[PersonFilmResponse]


class PersonListResponse(PaginatedResponse[PersonDetailResponse]):
    ...
