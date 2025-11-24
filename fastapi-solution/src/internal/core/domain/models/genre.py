import uuid
from typing import Optional

from internal.pkg.domain import BaseEntity
from internal.pkg.errors import ValueIsRequiredError


class Genre(BaseEntity[uuid.UUID]):
    def __init__(self,
                 name: str,
                 oid: Optional[uuid.UUID] = None,
                 description: Optional[str] = None):
        super().__init__(oid or uuid.uuid4())
        if not name:
            raise ValueIsRequiredError(param_name="name")
        self.name: str = name
        self.description: str = description
