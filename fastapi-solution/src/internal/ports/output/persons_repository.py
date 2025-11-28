import uuid
from typing import Protocol, List, Optional

from internal.core.domain.models.person import Person
from internal.pkg.pagination import PaginatedResult


class PersonRepository(Protocol):
    async def get_person_by_id(self, person_id: uuid.UUID) -> Person:
        pass

    async def get_all_persons(self) -> List[Person]:
        pass

    async def search_by_name(self, query: str, page: int, per_page: int) \
            -> PaginatedResult[Person]:
        pass


instance: Optional[PersonRepository] = None


def get_instance() -> PersonRepository:
    if instance is None:
        raise RuntimeError("Person repository is not initialized")
    return instance
