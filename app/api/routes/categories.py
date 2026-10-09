from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.category import (
    CategoryCreateRequest,
    CategoryDeleteRequest,
    CategoryOut,
    CategoryReorderRequest,
    CategoryUpdateRequest,
)
from app.services.category_service import CategoryService

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.post("/list", response_model=list[CategoryOut])
async def list_categories(payload: dict | None = Body(default={}), db: Session = Depends(get_db)):
    return CategoryService().list_categories(db)


@router.post("/create", response_model=CategoryOut)
async def create_category(payload: CategoryCreateRequest, db: Session = Depends(get_db)):
    return CategoryService().create_category(db, name=payload.name)


@router.post("/add", response_model=CategoryOut)
async def add_category(payload: CategoryCreateRequest, db: Session = Depends(get_db)):
    return CategoryService().create_category(db, name=payload.name)


@router.post("/new", response_model=CategoryOut)
async def new_category(payload: CategoryCreateRequest, db: Session = Depends(get_db)):
    return CategoryService().create_category(db, name=payload.name)


@router.post("/update", response_model=CategoryOut)
async def update_category(payload: CategoryUpdateRequest, db: Session = Depends(get_db)):
    return CategoryService().update_category(db, category_id=payload.id, name=payload.name)


@router.post("/reorder", response_model=list[CategoryOut])
async def reorder_categories(payload: CategoryReorderRequest, db: Session = Depends(get_db)):
    return CategoryService().reorder_categories(db, [item.model_dump() for item in payload.items])


@router.post("/delete")
async def delete_category(payload: CategoryDeleteRequest, db: Session = Depends(get_db)):
    return CategoryService().delete_category(db, payload.id)
