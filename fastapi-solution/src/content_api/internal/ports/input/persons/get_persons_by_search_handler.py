from dataclasses import dataclass
from typing import Protocol, Optional

from content_api.internal.core.domain.models.person import Person
from content_api.internal.pkg.pagination import Pagination, PaginatedResult


@dataclass(kw_only=True)
class SearchPersons(Pagination):
    query: str


class PersonsBySearchHandlerProtocol(Protocol):
    async def handle(self, query: SearchPersons) -> PaginatedResult[Person]:
        pass


instance: Optional[PersonsBySearchHandlerProtocol] = None

def get_instance() -> PersonsBySearchHandlerProtocol:
    if instance is None:
        raise RuntimeError("Search persons handler is not initialized")
    return instance
