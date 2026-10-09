from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    def list_all(self, db: Session) -> list[Category]:
        return db.execute(
            select(Category).order_by(Category.sort_order.asc(), Category.id.asc())
        ).scalars().all()

    def get_by_id(self, db: Session, category_id: int) -> Category | None:
        return db.get(Category, category_id)

    def create(self, db: Session, name: str, sort_order: int) -> Category:
        category = Category(category_name=name, sort_order=sort_order)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def update(self, db: Session, category: Category, name: str) -> Category:
        category.category_name = name
        category.updated_at = category.updated_at
        db.commit()
        db.refresh(category)
        return category

    def set_sort_orders(self, db: Session, items: list[tuple[int, int]]) -> None:
        for category_id, sort_order in items:
            category = db.get(Category, category_id)
            if category is not None:
                category.sort_order = sort_order
        db.commit()

    def delete(self, db: Session, category: Category) -> None:
        db.delete(category)
        db.commit()
