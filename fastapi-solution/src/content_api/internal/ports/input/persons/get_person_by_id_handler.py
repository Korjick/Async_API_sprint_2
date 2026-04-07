import uuid
from dataclasses import dataclass
from typing import Protocol, Optional

from content_api.internal.core.domain.models.person import Person


@dataclass(kw_only=True)
class GetPersonById:
    id: uuid.UUID


class PersonByIdHandlerProtocol(Protocol):
    async def handle(self, query: GetPersonById) -> Person:
        pass


instance: Optional[PersonByIdHandlerProtocol] = None


def get_instance() -> PersonByIdHandlerProtocol:
    if instance is None:
        raise RuntimeError("Person by id handler is not initialized")
    return instance
