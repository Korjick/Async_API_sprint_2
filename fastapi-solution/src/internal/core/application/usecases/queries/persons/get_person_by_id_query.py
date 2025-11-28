from internal.core.domain.models.person import Person
from internal.ports.input.persons.get_person_by_id_handler import \
    PersonByIdHandlerProtocol, GetPersonById
from internal.ports.output.persons_repository import PersonRepository


class GetPersonByIdUseCase(PersonByIdHandlerProtocol):
    def __init__(self, person_repository: PersonRepository):
        self.person_repository = person_repository

    async def handle(self, query: GetPersonById) -> Person:
        return await self.person_repository.get_person_by_id(query.id)
