from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class VideoListRequest(BaseModel):
    categoryId: int
    page: int = 0
    size: int = 20


class VideoSearchRequest(BaseModel):
    keyword: str
    page: int = 0
    size: int = 20


class VideoCreateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: str | None = None
    categoryId: int
    driveUrl: str = Field(..., min_length=1)


class VideoUpdateRequest(BaseModel):
    id: int
    title: str | None = None
    description: str | None = None
    categoryId: int | None = None


class VideoReorderItem(BaseModel):
    id: int
    sortOrder: int


class VideoReorderRequest(BaseModel):
    categoryId: int
    items: list[VideoReorderItem]


class VideoDeleteRequest(BaseModel):
    id: int


class VideoCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    thumbnailUrl: str | None = None
    playbackUrl: str | None = None


class VideoDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    categoryId: int | None = None
    thumbnailUrl: str | None = None
    playbackUrl: str | None = None


class VideoPaginatedResponse(BaseModel):
    items: list[VideoCard]
    page: int
    size: int
    totalElements: int
    totalPages: int


class VideoCreateResponse(VideoDetail):
    pass
