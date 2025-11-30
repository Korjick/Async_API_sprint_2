from typing import List

from internal.core.domain.models.person import Person
from internal.ports.input.persons.get_all_persons_handler import \
    AllPersonsHandlerProtocol, GetAllPersons
from internal.ports.output.persons_repository import PersonRepository


class GetAllPersonUseCase(AllPersonsHandlerProtocol):
    def __init__(self, person_repository: PersonRepository):
        self.person_repository = person_repository

    async def handle(self, query: GetAllPersons) -> List[Person]:
        return await self.person_repository.get_all_persons()