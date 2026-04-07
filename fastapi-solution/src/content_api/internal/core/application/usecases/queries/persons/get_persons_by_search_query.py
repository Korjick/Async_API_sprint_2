from content_api.internal.core.domain.models.person import Person
from content_api.internal.pkg.pagination import PaginatedResult
from content_api.internal.ports.input.persons.get_persons_by_search_handler import \
    PersonsBySearchHandlerProtocol, SearchPersons
from content_api.internal.ports.output.persons_repository import PersonRepository


class GetPersonsBySearchUseCase(PersonsBySearchHandlerProtocol):
    def __init__(self, person_repository: PersonRepository):
        self.person_repository = person_repository

    async def handle(self, query: SearchPersons) -> PaginatedResult[Person]:
        return await self.person_repository.search_by_name(
            query=query.query,
            page=query.page,
            per_page=query.per_page
        )
