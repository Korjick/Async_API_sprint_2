import uuid
from enum import Enum
from typing import Optional, List

from content_api.internal.core.domain.models.genre import Genre
from content_api.internal.core.domain.models.person import Person
from content_api.internal.pkg.domain import BaseAggregate
from content_api.internal.pkg.errors import ValueIsRequiredError


class SortBy(str, Enum):
    IMDB_RATING_DESC = "-imdb_rating"
    IMDB_RATING_ASC = "imdb_rating"
    TITLE_DESC = '-title'
    TITLE_ASC = 'title'


class Film(BaseAggregate[uuid.UUID]):
    def __init__(self,
                 title: str,
                 oid: Optional[uuid.UUID] = None,
                 description: Optional[str] = None,
                 imdb_rating: Optional[float] = None,
                 genres: List[Genre] = None,
                 actors: List[Person] = None,
                 writers: List[Person] = None,
                 directors: List[Person] = None):
        super().__init__(oid or uuid.uuid4())
        if not title:
            raise ValueIsRequiredError(param_name="title")
        self.title: str = title
        self.description: Optional[str] = description
        self.imdb_rating: Optional[float] = imdb_rating
        self.genres: List[Genre] = genres if genres is not None else []
        self.actors: List[Person] = actors if actors is not None else []
        self.writers: List[Person] = writers if writers is not None else []
        self.directors: List[Person] = (
            directors) if directors is not None else []
