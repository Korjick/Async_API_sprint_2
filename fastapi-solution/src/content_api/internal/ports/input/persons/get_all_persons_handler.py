from dataclasses import dataclass
from typing import Protocol, List, Optional

from content_api.internal.core.domain.models.person import Person


@dataclass(kw_only=True)
class GetAllPersons:
    pass


class AllPersonsHandlerProtocol(Protocol):
    async def handle(self, query: GetAllPersons) -> List[Person]:
        pass


instance: Optional[AllPersonsHandlerProtocol] = None

def get_instance() -> AllPersonsHandlerProtocol:
    if instance is None:
        raise RuntimeError("All persons handler is not initialized")
    return instance