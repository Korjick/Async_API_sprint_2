from dataclasses import dataclass
from typing import Protocol

from internal.core.domain.models.person import Person
from internal.pkg.pagination import Pagination, PaginatedResult
from internal.ports.persons_repository import PersonRepository


@dataclass(kw_only=True)
class SearchPersons(Pagination):
    query: str


class SearchPersonsHandlerProtocol(Protocol):
    async def handle(self, query: SearchPersons) -> PaginatedResult[Person]:
        pass


class SearchPersonsHandler:
    def __init__(self, person_repository: PersonRepository):
        self.person_repository = person_repository

    async def handle(self, query: SearchPersons) -> PaginatedResult[Person]:
        return await self.person_repository.search_by_name(
            query=query.query,
            page=query.page,
            per_page=query.per_page
        )
