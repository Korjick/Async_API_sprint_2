from typing import Generic, TypeVar, List

from pydantic import BaseModel, Field

SchemaT = TypeVar("SchemaT")


class PaginationRequest(BaseModel):
    page: int = Field(1, description="Page number", examples=[1])
    per_page: int = Field(20, description="Items per page", examples=[20])


class PaginatedResponse(PaginationRequest, Generic[SchemaT]):
    total: int = Field(..., description="Total number of items", examples=[142])
    items: List[SchemaT] = Field(..., description="Items on current page")
