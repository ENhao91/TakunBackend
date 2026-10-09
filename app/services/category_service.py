from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self) -> None:
        self.repository = CategoryRepository()

    def list_categories(self, db: Session):
        rows = self.repository.list_all(db)
        return [{"id": row.id, "name": row.category_name, "sortOrder": row.sort_order} for row in rows]

    def create_category(self, db: Session, *, name: str):
        cleaned = (name or "").strip()
        if not cleaned:
            raise HTTPException(status_code=400, detail="分類名稱不可為空白。")

        existing = db.execute(select(Category).where(Category.category_name.ilike(cleaned))).scalars().first()
        if existing:
            raise HTTPException(status_code=409, detail="分類名稱已存在。")

        next_sort_order = (db.execute(select(Category.sort_order).order_by(Category.sort_order.desc()).limit(1)).scalar() or 0) + 1
        category = self.repository.create(db, cleaned, next_sort_order)
        return {"id": category.id, "name": category.category_name, "sortOrder": category.sort_order}

    def update_category(self, db: Session, *, category_id: int, name: str):
        category = self.repository.get_by_id(db, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="分類不存在。")
        cleaned = (name or "").strip()
        if not cleaned:
            raise HTTPException(status_code=400, detail="分類名稱不可為空白。")

        existing = db.execute(select(Category).where(Category.id != category_id, Category.category_name.ilike(cleaned))).scalars().first()
        if existing:
            raise HTTPException(status_code=409, detail="分類名稱已存在。")

        updated = self.repository.update(db, category, cleaned)
        return {"id": updated.id, "name": updated.category_name, "sortOrder": updated.sort_order}

    def reorder_categories(self, db: Session, items: list[dict]):
        category_ids = [item["id"] for item in items]
        existing = db.execute(select(Category.id)).scalars().all()
        if set(category_ids) != set(existing):
            raise HTTPException(status_code=400, detail="排序資料包含不存在的分類。")

        ordered = [(item["id"], int(item["sortOrder"])) for item in items]
        self.repository.set_sort_orders(db, ordered)
        return self.list_categories(db)

    def delete_category(self, db: Session, category_id: int):
        category = self.repository.get_by_id(db, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="分類不存在。")

        from app.models.video import Video

        has_videos = db.execute(select(Video.id).where(Video.category_id == category_id).limit(1)).scalar() is not None
        if has_videos:
            raise HTTPException(status_code=409, detail="分類底下仍有影片，無法刪除。")

        self.repository.delete(db, category)
        return {"message": "分類已刪除。"}
