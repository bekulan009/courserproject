from fastapi import APIRouter, HTTPException, Depends
from mysite.database.models import Enrollment, User, StudyGroup
from mysite.database.schemas import EnrollmentOutSchema, EnrollmentInputSchema, EnrollmentUpdateSchema
from mysite.database.db import get_db
from sqlalchemy.orm import Session
from typing import List

enrollment_router = APIRouter(prefix='/enrollment', tags=['Enrollment'])


@enrollment_router.post('/', response_model=EnrollmentOutSchema)
async def create_enrollment(enrollment: EnrollmentInputSchema, db: Session = Depends(get_db)):
    student = db.query(User).filter(User.id == enrollment.student_id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Студент не найден")

    group = db.query(StudyGroup).filter(StudyGroup.id == enrollment.group_id).first()
    if not group:
        raise HTTPException(status_code=400, detail="Группа не найдена")

    enrollment_db = Enrollment(**enrollment.model_dump())
    db.add(enrollment_db)
    db.commit()
    db.refresh(enrollment_db)
    return enrollment_db


@enrollment_router.get('/', response_model=List[EnrollmentOutSchema])
async def list_enrollments(db: Session = Depends(get_db)):
    return db.query(Enrollment).all()


@enrollment_router.get('/{enrollment_id}/', response_model=EnrollmentOutSchema)
async def detail_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    enrollment_db = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment_db:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return enrollment_db


@enrollment_router.put('/{enrollment_id}/', response_model=dict)
async def update_enrollment(enrollment_id: int, enrollment: EnrollmentUpdateSchema, db: Session = Depends(get_db)):
    enrollment_db = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment_db:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    update_data = enrollment.model_dump(exclude_unset=True)

    if "student_id" in update_data:
        student = db.query(User).filter(User.id == update_data["student_id"]).first()
        if not student:
            raise HTTPException(status_code=400, detail="Студент не найден")

    if "group_id" in update_data:
        group = db.query(StudyGroup).filter(StudyGroup.id == update_data["group_id"]).first()
        if not group:
            raise HTTPException(status_code=400, detail="Группа не найдена")

    for key, value in update_data.items():
        setattr(enrollment_db, key, value)

    db.commit()
    db.refresh(enrollment_db)
    return {"message": "Запись изменена"}


@enrollment_router.delete('/{enrollment_id}/', response_model=dict)
async def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    enrollment_db = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment_db:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    db.delete(enrollment_db)
    db.commit()
    return {"message": "Запись удалена"}
