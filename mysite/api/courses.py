from fastapi import APIRouter, HTTPException, Depends
from mysite.database.models import Course, Category
from mysite.database.schemas import CourseOutSchema, CourseInputSchema, CourseUpdateSchema
from mysite.database.db import get_db
from sqlalchemy.orm import Session
from typing import List

course_router = APIRouter(prefix='/course', tags=['Course'])


@course_router.post('/', response_model=CourseOutSchema)
async def create_course(course: CourseInputSchema, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == course.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Указанная категория не найдена")

    course_db = Course(**course.model_dump())
    db.add(course_db)
    db.commit()
    db.refresh(course_db)
    return course_db


@course_router.get('/', response_model=List[CourseOutSchema])
async def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()


@course_router.get('/{course_id}/', response_model=CourseOutSchema)
async def detail_course(course_id: int, db: Session = Depends(get_db)):
    course_db = db.query(Course).filter(Course.id == course_id).first()
    if not course_db:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return course_db


@course_router.put('/{course_id}/', response_model=dict)
async def update_course(course_id: int, course: CourseUpdateSchema, db: Session = Depends(get_db)):
    course_db = db.query(Course).filter(Course.id == course_id).first()
    if not course_db:
        raise HTTPException(status_code=404, detail="Курс не найден")

    update_data = course.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=400, detail="Указанная категория не найдена")

    for key, value in update_data.items():
        setattr(course_db, key, value)

    db.commit()
    db.refresh(course_db)
    return {"message": "Курс изменен"}


@course_router.delete('/{course_id}/', response_model=dict)
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    course_db = db.query(Course).filter(Course.id == course_id).first()
    if not course_db:
        raise HTTPException(status_code=404, detail="Курс не найден")

    db.delete(course_db)
    db.commit()
    return {"message": "Курс удален"}
