from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from mysite.database.models import (
    StudyGroup,
    Course,
    User,
    Enrollment,
    StudyGroupStatusChoices,
    EnrollmentStatusChoices,
)
from mysite.database.schemas import (
    StudyGroupOutSchema,
    StudyGroupInputSchema,
    StudyGroupUpdateSchema,
    EnrollmentOutSchema,
)
from mysite.database.db import get_db
from mysite.auth import get_current_user, get_current_teacher, get_current_student

study_group_router = APIRouter(prefix="/study_group", tags=["StudyGroup"])


@study_group_router.post("/", response_model=StudyGroupOutSchema)
async def create_study_group(
    group: StudyGroupInputSchema,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher),
):
    course = db.query(Course).filter(Course.id == group.course_id).first()
    if not course:
        raise HTTPException(status_code=400, detail="Курс не найден")

    teacher_user = db.query(User).filter(User.id == group.teacher_id).first()
    if not teacher_user:
        raise HTTPException(status_code=400, detail="Преподаватель не найден")

    group_db = StudyGroup(**group.model_dump())
    db.add(group_db)
    db.commit()
    db.refresh(group_db)
    return group_db


@study_group_router.post("/{group_id}/join/", response_model=EnrollmentOutSchema)
async def join_study_group(
    group_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(get_current_student),
):
    """Студент записывается в группу. Проверяется статус 'recruiting' и лимит мест (capacity)."""
    group = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    # 1. Проверка статуса группы: должен быть только recruiting
    if group.status != StudyGroupStatusChoices.recruiting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Запись в данную группу не ведется. Текущий статус группы: '{group.status.value}' (требуется 'recruiting')",
        )

    # 2. Проверка количества уже записанных студентов vs capacity
    active_enrollments_count = (
        db.query(Enrollment)
        .filter(
            Enrollment.group_id == group.id,
            Enrollment.status == EnrollmentStatusChoices.active,
        )
        .count()
    )
    if active_enrollments_count >= group.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"В группе нет свободных мест! Вместимость группы: {group.capacity}, занято: {active_enrollments_count}",
        )

    # 3. Проверка на повторную запись того же студента
    already_enrolled = (
        db.query(Enrollment)
        .filter(
            Enrollment.group_id == group.id,
            Enrollment.student_id == student.id,
            Enrollment.status == EnrollmentStatusChoices.active,
        )
        .first()
    )
    if already_enrolled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже записаны в эту группу",
        )

    new_enrollment = Enrollment(
        student_id=student.id,
        group_id=group.id,
        status=EnrollmentStatusChoices.active,
    )
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return new_enrollment


@study_group_router.get("/", response_model=List[StudyGroupOutSchema])
async def list_study_groups(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(StudyGroup).all()


@study_group_router.get("/{group_id}/", response_model=StudyGroupOutSchema)
async def detail_study_group(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    group_db = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group_db:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return group_db


@study_group_router.put("/{group_id}/", response_model=dict)
async def update_study_group(
    group_id: int,
    group: StudyGroupUpdateSchema,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher),
):
    group_db = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group_db:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    update_data = group.model_dump(exclude_unset=True)

    if "course_id" in update_data:
        course = db.query(Course).filter(Course.id == update_data["course_id"]).first()
        if not course:
            raise HTTPException(status_code=400, detail="Курс не найден")

    if "teacher_id" in update_data:
        teacher_user = db.query(User).filter(User.id == update_data["teacher_id"]).first()
        if not teacher_user:
            raise HTTPException(status_code=400, detail="Преподаватель не найден")

    for key, value in update_data.items():
        setattr(group_db, key, value)

    db.commit()
    db.refresh(group_db)
    return {"message": "Группа изменена"}


@study_group_router.delete("/{group_id}/", response_model=dict)
async def delete_study_group(
    group_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher),
):
    group_db = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group_db:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    db.delete(group_db)
    db.commit()
    return {"message": "Группа удалена"}
