from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.video import (
    VideoCreateRequest,
    VideoDeleteRequest,
    VideoDetail,
    VideoListRequest,
    VideoPaginatedResponse,
    VideoReorderRequest,
    VideoSearchRequest,
    VideoUpdateRequest,
)
from app.services.video_service import VideoService

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.post("/list", response_model=VideoPaginatedResponse)
async def list_videos(payload: VideoListRequest, db: Session = Depends(get_db)):
    return VideoService().list_videos(db, category_id=payload.categoryId, page=payload.page, size=payload.size)


@router.post("/search", response_model=VideoPaginatedResponse)
async def search_videos(payload: VideoSearchRequest, db: Session = Depends(get_db)):
    return VideoService().search_videos(db, keyword=payload.keyword, page=payload.page, size=payload.size)


@router.post("/detail", response_model=VideoDetail)
async def detail_video(payload: dict, db: Session = Depends(get_db)):
    video_id = int(payload.get("videoId"))
    return VideoService().get_video_detail(db, video_id=video_id)


@router.post("/create", response_model=VideoDetail)
async def create_video(payload: VideoCreateRequest, db: Session = Depends(get_db)):
    return VideoService().create_video(
        db,
        title=payload.title,
        description=payload.description,
        category_id=payload.categoryId,
        drive_url=payload.driveUrl,
    )


@router.post("/update", response_model=VideoDetail)
async def update_video(payload: VideoUpdateRequest, db: Session = Depends(get_db)):
    return VideoService().update_video(
        db,
        video_id=payload.id,
        title=payload.title,
        description=payload.description,
        category_id=payload.categoryId,
    )


@router.post("/reorder", response_model=VideoPaginatedResponse)
async def reorder_videos(payload: VideoReorderRequest, db: Session = Depends(get_db)):
    return VideoService().reorder_videos(db, category_id=payload.categoryId, items=[item.model_dump() for item in payload.items])


@router.post("/delete")
async def delete_video(payload: VideoDeleteRequest, db: Session = Depends(get_db)):
    return VideoService().delete_video(db, video_id=payload.id)
