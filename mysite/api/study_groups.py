from fastapi import APIRouter, HTTPException, Depends
from mysite.database.models import StudyGroup, Course, User, UserRoleChoices
from mysite.database.schemas import StudyGroupOutSchema, StudyGroupInputSchema, StudyGroupUpdateSchema
from mysite.database.db import get_db
from sqlalchemy.orm import Session
from typing import List

study_group_router = APIRouter(prefix='/study_group', tags=['StudyGroup'])


@study_group_router.post('/', response_model=StudyGroupOutSchema)
async def create_study_group(group: StudyGroupInputSchema, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == group.course_id).first()
    if not course:
        raise HTTPException(status_code=400, detail="Курс не найден")

    teacher = db.query(User).filter(User.id == group.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=400, detail="Преподаватель не найден")

    group_db = StudyGroup(**group.model_dump())
    db.add(group_db)
    db.commit()
    db.refresh(group_db)
    return group_db


@study_group_router.get('/', response_model=List[StudyGroupOutSchema])
async def list_study_groups(db: Session = Depends(get_db)):
    return db.query(StudyGroup).all()


@study_group_router.get('/{group_id}/', response_model=StudyGroupOutSchema)
async def detail_study_group(group_id: int, db: Session = Depends(get_db)):
    group_db = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group_db:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return group_db


@study_group_router.put('/{group_id}/', response_model=dict)
async def update_study_group(group_id: int, group: StudyGroupUpdateSchema, db: Session = Depends(get_db)):
    group_db = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group_db:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    update_data = group.model_dump(exclude_unset=True)

    if "course_id" in update_data:
        course = db.query(Course).filter(Course.id == update_data["course_id"]).first()
        if not course:
            raise HTTPException(status_code=400, detail="Курс не найден")

    if "teacher_id" in update_data:
        teacher = db.query(User).filter(User.id == update_data["teacher_id"]).first()
        if not teacher:
            raise HTTPException(status_code=400, detail="Преподаватель не найден")

    for key, value in update_data.items():
        setattr(group_db, key, value)

    db.commit()
    db.refresh(group_db)
    return {"message": "Группа изменена"}


@study_group_router.delete('/{group_id}/', response_model=dict)
async def delete_study_group(group_id: int, db: Session = Depends(get_db)):
    group_db = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group_db:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    db.delete(group_db)
    db.commit()
    return {"message": "Группа удалена"}
