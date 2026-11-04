from fastapi import APIRouter, HTTPException, Depends
from mysite.database.models import User
from mysite.database.schemas import UserOutSchema, UserInputSchema, UserUpdateSchema
from mysite.database.db import get_db
from sqlalchemy.orm import Session
from typing import List

user_router = APIRouter(prefix='/user', tags=['User'])


@user_router.post('/', response_model=UserOutSchema)
async def create_user(user: UserInputSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    user_db = User(**user.model_dump())
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


@user_router.get('/', response_model=List[UserOutSchema])
async def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@user_router.get('/{user_id}/', response_model=UserOutSchema)
async def detail_user(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user_db


@user_router.put('/{user_id}/', response_model=dict)
async def update_user(user_id: int, user: UserUpdateSchema, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    update_data = user.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_db, key, value)

    db.commit()
    db.refresh(user_db)
    return {"message": "Пользователь изменен"}


@user_router.delete('/{user_id}/', response_model=dict)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    db.delete(user_db)
    db.commit()
    return {"message": "Пользователь удален"}
