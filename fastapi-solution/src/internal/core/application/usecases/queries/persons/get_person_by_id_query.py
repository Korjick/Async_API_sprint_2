import uuid
from dataclasses import dataclass
from typing import Protocol, Optional

from internal.core.domain.models.person import Person
from internal.ports.persons_repository import PersonRepository


@dataclass(kw_only=True)
class GetPersonById:
    id: uuid.UUID


class GetPersonByIdHandlerProtocol(Protocol):
    async def handle(self, query: GetPersonById) -> Optional[Person]:
        pass


class GetPersonByIdHandler:
    def __init__(self, person_repository: PersonRepository):
        self.person_repository = person_repository

    async def handle(self, query: GetPersonById) -> Optional[Person]:
        return await self.person_repository.get_person_by_id(query.id)
