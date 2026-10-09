from __future__ import annotations

from math import ceil
import re
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.video import Video
from app.repositories.video_repository import VideoRepository


class VideoService:
    def __init__(self) -> None:
        self.repository = VideoRepository()

    def _normalize_page_size(self, page: int, size: int) -> tuple[int, int]:
        if page < 0:
            raise HTTPException(status_code=400, detail="頁碼不可小於 0。")
        if size <= 0 or size > 200:
            raise HTTPException(status_code=400, detail="每頁筆數必須介於 1 和 200 之間。")
        return page, size

    def _playback_url(self, drive_url: str) -> str:
        if not drive_url:
            return ""
        if drive_url.startswith("https://"):
            return drive_url
        return f"https://drive.google.com/file/d/{drive_url}/preview"

    def _validate_drive_url(self, drive_url: str) -> str:
        cleaned = drive_url.strip()
        parsed = urlparse(cleaned)
        if parsed.scheme != "https" or parsed.hostname != "drive.google.com":
            raise HTTPException(status_code=400, detail="請提供有效的 Google Drive 影片分享網址。")

        path_id = re.search(r"^/file/d/([A-Za-z0-9_-]+)(?:/|$)", parsed.path)
        query_id = parse_qs(parsed.query).get("id", [None])[0]
        if not path_id and not (query_id and re.fullmatch(r"[A-Za-z0-9_-]+", query_id)):
            raise HTTPException(status_code=400, detail="Google Drive 網址格式無效，請使用檔案分享連結。")
        return cleaned

    def list_videos(self, db: Session, *, category_id: int, page: int, size: int):
        category = db.get(Category, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="分類不存在。")

        page, size = self._normalize_page_size(page, size)
        items, total = self.repository.get_by_category(db, category_id, page, size)
        payload = {
            "items": [
                {
                    "id": row.id,
                    "title": row.title,
                    "description": row.description,
                    "thumbnailUrl": None,
                    "playbackUrl": self._playback_url(row.drive_url),
                }
                for row in items
            ],
            "page": page,
            "size": size,
            "totalElements": total,
            "totalPages": 0 if total == 0 else ceil(total / size),
        }
        return payload

    def search_videos(self, db: Session, *, keyword: str, page: int, size: int):
        cleaned = (keyword or "").strip()
        if not cleaned:
            raise HTTPException(status_code=400, detail="關鍵字不可為空白。")

        page, size = self._normalize_page_size(page, size)
        items, total = self.repository.search(db, cleaned, page, size)
        payload = {
            "items": [
                {
                    "id": row.id,
                    "title": row.title,
                    "description": row.description,
                    "thumbnailUrl": None,
                    "playbackUrl": self._playback_url(row.drive_url),
                }
                for row in items
            ],
            "page": page,
            "size": size,
            "totalElements": total,
            "totalPages": 0 if total == 0 else ceil(total / size),
        }
        return payload

    def get_video_detail(self, db: Session, *, video_id: int):
        video = self.repository.get_by_id(db, video_id)
        if video is None:
            raise HTTPException(status_code=404, detail="影片不存在。")

        return {
            "id": video.id,
            "title": video.title,
            "description": video.description,
            "categoryId": video.category_id,
            "thumbnailUrl": None,
            "playbackUrl": self._playback_url(video.drive_url),
        }

    def create_video(self, db: Session, *, title: str, description: str | None, category_id: int, drive_url: str):
        cleaned_title = (title or "").strip()
        if not cleaned_title:
            raise HTTPException(status_code=400, detail="影片標題不可為空白。")
        cleaned_drive_url = self._validate_drive_url(drive_url)

        category = db.get(Category, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="分類不存在。")

        next_sort_order = (db.execute(select(Video.sort_order).where(Video.category_id == category_id).order_by(Video.sort_order.desc()).limit(1)).scalar() or 0) + 1
        created = self.repository.create(
            db,
            title=cleaned_title,
            description=description.strip() if isinstance(description, str) and description.strip() else None,
            category_id=category_id,
            drive_url=cleaned_drive_url,
            sort_order=next_sort_order,
        )
        return self.get_video_detail(db, video_id=created.id)

    def update_video(self, db: Session, *, video_id: int, title: str | None, description: str | None, category_id: int | None):
        video = self.repository.get_by_id(db, video_id)
        if video is None:
            raise HTTPException(status_code=404, detail="影片不存在。")

        original_category_id = video.category_id

        if title is not None:
            cleaned_title = title.strip()
            if not cleaned_title:
                raise HTTPException(status_code=400, detail="影片標題不可為空白。")
            title = cleaned_title

        if category_id is not None:
            target_category = db.get(Category, category_id)
            if target_category is None:
                raise HTTPException(status_code=404, detail="目標分類不存在。")

        if description is not None and description.strip() == "":
            description = None

        updated = self.repository.update(db, video, title=title, description=description, category_id=category_id)
        if category_id is not None and category_id != original_category_id:
            max_sort = db.execute(select(Video.sort_order).where(Video.category_id == category_id).order_by(Video.sort_order.desc()).limit(1)).scalar() or 0
            updated.sort_order = max_sort + 1
            db.commit()
        return self.get_video_detail(db, video_id=updated.id)

    def reorder_videos(self, db: Session, *, category_id: int, items: list[dict]):
        category = db.get(Category, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="分類不存在。")

        for item in items:
            video = db.get(Video, item["id"])
            if video is None or video.category_id != category_id:
                raise HTTPException(status_code=400, detail="排序資料包含不屬於此分類的影片。")
            video.sort_order = int(item["sortOrder"])
        db.commit()
        return self.list_videos(db, category_id=category_id, page=0, size=max(1, len(items)))

    def delete_video(self, db: Session, *, video_id: int):
        video = self.repository.get_by_id(db, video_id)
        if video is None:
            raise HTTPException(status_code=404, detail="影片不存在。")
        self.repository.delete(db, video)
        return {"message": "影片已刪除。"}
