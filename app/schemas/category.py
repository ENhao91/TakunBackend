from pydantic import BaseModel, ConfigDict, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)


class CategoryUpdateRequest(BaseModel):
    id: int
    name: str = Field(..., min_length=1)


class CategoryReorderItem(BaseModel):
    id: int
    sortOrder: int


class CategoryReorderRequest(BaseModel):
    items: list[CategoryReorderItem]


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sortOrder: int


class CategoryDeleteRequest(BaseModel):
    id: int
