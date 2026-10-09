from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.video import Video


class VideoRepository:
    def get_by_category(self, db: Session, category_id: int, page: int, size: int) -> tuple[list[Video], int]:
        query = select(Video).where(Video.category_id == category_id).order_by(Video.sort_order.asc(), Video.id.asc())
        total = db.scalar(select(func.count()).select_from(query.subquery()))
        items = db.execute(query.offset(page * size).limit(size)).scalars().all()
        return items, total or 0

    def search(self, db: Session, keyword: str, page: int, size: int) -> tuple[list[Video], int]:
        like = f"%{keyword}%"
        query = (
            select(Video)
            .where(Video.title.ilike(like))
            .order_by(Video.sort_order.asc(), Video.id.asc())
        )
        total = db.scalar(select(func.count()).select_from(query.subquery()))
        items = db.execute(query.offset(page * size).limit(size)).scalars().all()
        return items, total or 0

    def get_by_id(self, db: Session, video_id: int) -> Video | None:
        return db.get(Video, video_id)

    def create(self, db: Session, *, title: str, description: str | None, category_id: int, drive_url: str, sort_order: int) -> Video:
        video = Video(
            title=title,
            description=description,
            category_id=category_id,
            drive_url=drive_url,
            sort_order=sort_order,
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        return video

    def update(self, db: Session, video: Video, *, title: str | None, description: str | None, category_id: int | None) -> Video:
        if title is not None:
            video.title = title
        if description is not None:
            video.description = description
        if category_id is not None:
            video.category_id = category_id
        db.commit()
        db.refresh(video)
        return video

    def delete(self, db: Session, video: Video) -> None:
        db.delete(video)
        db.commit()

    def list_by_category_for_reorder(self, db: Session, category_id: int) -> list[Video]:
        return db.execute(select(Video).where(Video.category_id == category_id).order_by(Video.sort_order.asc(), Video.id.asc())).scalars().all()

    def count_by_category(self, db: Session, category_id: int) -> int:
        return db.scalar(select(func.count(Video.id)).where(Video.category_id == category_id)) or 0
