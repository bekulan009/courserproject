from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from mysite.database.models import Application, User, Course, CourseStatusChoices
from mysite.database.schemas import (
    ApplicationOutSchema,
    ApplicationInputSchema,
    ApplicationUpdateSchema,
)
from mysite.database.db import get_db
from mysite.auth import get_current_student, get_current_manager

application_router = APIRouter(prefix="/application", tags=["Application"])


@application_router.post("/", response_model=ApplicationOutSchema)
async def create_application(
    app_data: ApplicationInputSchema,
    db: Session = Depends(get_db),
    student: User = Depends(get_current_student),
):
    course = db.query(Course).filter(Course.id == app_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    if not course.is_active:
        raise HTTPException(status_code=400, detail="Курс в данный момент неактивен")

    # Проверка условий пользователя:
    # student.is_active == True -> разрешено
    # student.is_active == False -> разрешено ТОЛЬКО если course.status == free
    if not student.is_active:
        if course.status != CourseStatusChoices.free:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неактивный студент может подавать заявку только на бесплатные курсы (course.status == 'free')",
            )

    # Проверка на повторную активную заявку на этот же курс
    existing_app = (
        db.query(Application)
        .filter(
            Application.student_id == student.id,
            Application.course_id == course.id,
            Application.status.in_(["new", "in_progress", "accepted"]),
        )
        .first()
    )
    if existing_app:
        raise HTTPException(
            status_code=400,
            detail=f"У вас уже есть активная заявка #{existing_app.id} на этот курс со статусом '{existing_app.status.value}'",
        )

    application_dict = app_data.model_dump()
    # student_id всегда берется из авторизованного студента
    application_dict["student_id"] = student.id

    application_db = Application(**application_dict)
    db.add(application_db)
    db.commit()
    db.refresh(application_db)
    return application_db


@application_router.get("/", response_model=List[ApplicationOutSchema])
async def list_applications(
    db: Session = Depends(get_db),
    manager: User = Depends(get_current_manager),
):
    """Список всех заявок доступен только менеджерам"""
    return db.query(Application).all()


@application_router.get("/{application_id}/", response_model=ApplicationOutSchema)
async def detail_application(
    application_id: int,
    db: Session = Depends(get_db),
    manager: User = Depends(get_current_manager),
):
    """Детали заявки доступны только менеджеру"""
    application_db = db.query(Application).filter(Application.id == application_id).first()
    if not application_db:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return application_db


@application_router.put("/{application_id}/", response_model=dict)
async def update_application(
    application_id: int,
    app_data: ApplicationUpdateSchema,
    db: Session = Depends(get_db),
    manager: User = Depends(get_current_manager),
):
    """Обновление заявки (статус, комментарий, назначение менеджера) менеджером"""
    application_db = db.query(Application).filter(Application.id == application_id).first()
    if not application_db:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    update_data = app_data.model_dump(exclude_unset=True)

    # По умолчанию менеджер может назначить себя ответственным
    if "manager_id" not in update_data and application_db.manager_id is None:
        application_db.manager_id = manager.id

    for key, value in update_data.items():
        setattr(application_db, key, value)

    db.commit()
    db.refresh(application_db)
    return {"message": "Заявка успешно обновлена"}


@application_router.delete("/{application_id}/", response_model=dict)
async def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    manager: User = Depends(get_current_manager),
):
    """Удаление заявки менеджером"""
    application_db = db.query(Application).filter(Application.id == application_id).first()
    if not application_db:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    db.delete(application_db)
    db.commit()
    return {"message": "Заявка удалена"}
