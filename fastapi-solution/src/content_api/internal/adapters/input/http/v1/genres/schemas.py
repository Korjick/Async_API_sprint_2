from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from content_api.internal.core.domain.models.genre import Genre

class GenreResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    uuid: str = Field(alias="id")
    name: str
    description: Optional[str] = None

    @classmethod
    def from_domain(cls, genre: Genre):
        return cls(
            id=str(genre.id),
            name=genre.name,
            description=genre.description
        )

class GenreListResponse(BaseModel):
    items: List[GenreResponse]
