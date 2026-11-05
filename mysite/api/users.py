from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from mysite.database.models import User
from mysite.database.schemas import (
    UserOutSchema,
    UserInputSchema,
    UserUpdateSchema,
    UserRegisterSchema,
    UserLoginSchema,
    TokenSchema,
)
from mysite.database.db import get_db
from mysite.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_current_admin,
)

user_router = APIRouter(prefix="/user", tags=["User & Auth"])


@user_router.post("/register/", response_model=UserOutSchema)
async def register(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    user_dict = user_data.model_dump()
    user_dict["password"] = hash_password(user_dict["password"])
    new_user = User(**user_dict)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@user_router.post("/login/", response_model=TokenSchema)
async def login(credentials: UserLoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@user_router.post("/login-token", response_model=TokenSchema)
async def login_for_swagger_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Эндпоинт для кнопки 'Authorize' в Swagger UI (username принимает email)"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@user_router.get("/me/", response_model=UserOutSchema)
async def read_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@user_router.post("/", response_model=UserOutSchema)
async def create_user(
    user: UserInputSchema,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user_dict["password"])
    user_db = User(**user_dict)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


@user_router.get("/", response_model=List[UserOutSchema])
async def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(User).all()


@user_router.get("/{user_id}/", response_model=UserOutSchema)
async def detail_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user_db


@user_router.put("/{user_id}/", response_model=dict)
async def update_user(
    user_id: int,
    user: UserUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Только сам пользователь или админ может изменять данные
    if current_user.id != user_db.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения пользователя")

    update_data = user.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password"] = hash_password(update_data["password"])

    for key, value in update_data.items():
        setattr(user_db, key, value)

    db.commit()
    db.refresh(user_db)
    return {"message": "Пользователь изменен"}


@user_router.delete("/{user_id}/", response_model=dict)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    db.delete(user_db)
    db.commit()
    return {"message": "Пользователь удален"}
