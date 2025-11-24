import uuid
from typing import Optional

from internal.pkg.domain import BaseEntity
from internal.pkg.errors import ValueIsRequiredError


class Person(BaseEntity[uuid.UUID]):
    def __init__(self,
                 full_name: str,
                 oid: Optional[uuid.UUID] = None):
        super().__init__(oid or uuid.uuid4())
        if not full_name:
            raise ValueIsRequiredError(param_name="full_name")
        self.full_name: str = full_name
