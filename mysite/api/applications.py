from fastapi import APIRouter, HTTPException, Depends
from mysite.database.models import Application, User, Course
from mysite.database.schemas import ApplicationOutSchema, ApplicationInputSchema, ApplicationUpdateSchema
from mysite.database.db import get_db
from sqlalchemy.orm import Session
from typing import List

application_router = APIRouter(prefix='/application', tags=['Application'])


@application_router.post('/', response_model=ApplicationOutSchema)
async def create_application(app_data: ApplicationInputSchema, db: Session = Depends(get_db)):
    student = db.query(User).filter(User.id == app_data.student_id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Студент не найден")

    course = db.query(Course).filter(Course.id == app_data.course_id).first()
    if not course:
        raise HTTPException(status_code=400, detail="Курс не найден")

    if app_data.manager_id is not None:
        manager = db.query(User).filter(User.id == app_data.manager_id).first()
        if not manager:
            raise HTTPException(status_code=400, detail="Менеджер не найден")

    application_db = Application(**app_data.model_dump())
    db.add(application_db)
    db.commit()
    db.refresh(application_db)
    return application_db


@application_router.get('/', response_model=List[ApplicationOutSchema])
async def list_applications(db: Session = Depends(get_db)):
    return db.query(Application).all()


@application_router.get('/{application_id}/', response_model=ApplicationOutSchema)
async def detail_application(application_id: int, db: Session = Depends(get_db)):
    application_db = db.query(Application).filter(Application.id == application_id).first()
    if not application_db:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return application_db


@application_router.put('/{application_id}/', response_model=dict)
async def update_application(application_id: int, app_data: ApplicationUpdateSchema, db: Session = Depends(get_db)):
    application_db = db.query(Application).filter(Application.id == application_id).first()
    if not application_db:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    update_data = app_data.model_dump(exclude_unset=True)

    if "student_id" in update_data:
        student = db.query(User).filter(User.id == update_data["student_id"]).first()
        if not student:
            raise HTTPException(status_code=400, detail="Студент не найден")

    if "course_id" in update_data:
        course = db.query(Course).filter(Course.id == update_data["course_id"]).first()
        if not course:
            raise HTTPException(status_code=400, detail="Курс не найден")

    if update_data.get("manager_id") is not None:
        manager = db.query(User).filter(User.id == update_data["manager_id"]).first()
        if not manager:
            raise HTTPException(status_code=400, detail="Менеджер не найден")

    for key, value in update_data.items():
        setattr(application_db, key, value)

    db.commit()
    db.refresh(application_db)
    return {"message": "Заявка изменена"}


@application_router.delete('/{application_id}/', response_model=dict)
async def delete_application(application_id: int, db: Session = Depends(get_db)):
    application_db = db.query(Application).filter(Application.id == application_id).first()
    if not application_db:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    db.delete(application_db)
    db.commit()
    return {"message": "Заявка удалена"}
