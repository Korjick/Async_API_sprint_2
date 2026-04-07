from dataclasses import dataclass
from typing import Protocol, List, Optional

from content_api.internal.core.domain.models.genre import Genre


@dataclass(kw_only=True)
class GetAllGenres:
    pass


class AllGenresHandlerProtocol(Protocol):
    async def handle(self, query: GetAllGenres) -> List[Genre]:
        pass


instance: Optional[AllGenresHandlerProtocol] = None

def get_instance() -> AllGenresHandlerProtocol:
    if instance is None:
        raise RuntimeError("All genres handler is not initialized")
    return instance
