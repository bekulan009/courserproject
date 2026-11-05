from fastapi import APIRouter, HTTPException, Depends
from mysite.database.models import Category, User
from mysite.database.schemas import CategoryOutSchema, CategoryInputSchema, CategoryUpdateSchema
from mysite.database.db import get_db
from mysite.auth import get_current_admin
from sqlalchemy.orm import Session
from typing import List

category_router = APIRouter(prefix="/category", tags=["Category"])


@category_router.post("/", response_model=CategoryOutSchema)
async def create_category(
    category: CategoryInputSchema,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    existing = db.query(Category).filter(Category.category_name == category.category_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Категория с таким именем уже существует")
    category_db = Category(**category.model_dump())
    db.add(category_db)
    db.commit()
    db.refresh(category_db)
    return category_db


@category_router.get("/", response_model=List[CategoryOutSchema])
async def list_categories(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return db.query(Category).all()


@category_router.get("/{category_id}/", response_model=CategoryOutSchema)
async def detail_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    category_db = db.query(Category).filter(Category.id == category_id).first()
    if not category_db:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category_db


@category_router.put("/{category_id}/", response_model=dict)
async def update_category(
    category_id: int,
    category: CategoryUpdateSchema,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    category_db = db.query(Category).filter(Category.id == category_id).first()
    if not category_db:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    update_data = category.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category_db, key, value)

    db.commit()
    db.refresh(category_db)
    return {"message": "Категория изменена"}


@category_router.delete("/{category_id}/", response_model=dict)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    category_db = db.query(Category).filter(Category.id == category_id).first()
    if not category_db:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    db.delete(category_db)
    db.commit()
    return {"message": "Категория удалена"}
