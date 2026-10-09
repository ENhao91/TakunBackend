from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    message: str


class PaginationMeta(BaseModel):
    page: int = Field(ge=0)
    size: int = Field(ge=1)
    totalElements: int
    totalPages: int


class SuccessMessage(BaseModel):
    message: str
