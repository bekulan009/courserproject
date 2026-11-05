from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from mysite.database.models import (
    Enrollment,
    User,
    StudyGroup,
    UserRoleChoices,
    StudyGroupStatusChoices,
    EnrollmentStatusChoices,
)
from mysite.database.schemas import (
    EnrollmentOutSchema,
    EnrollmentInputSchema,
    EnrollmentUpdateSchema,
)
from mysite.database.db import get_db
from mysite.auth import get_current_user

enrollment_router = APIRouter(prefix="/enrollment", tags=["Enrollment"])


@enrollment_router.post("/", response_model=EnrollmentOutSchema)
async def create_enrollment(
    enrollment: EnrollmentInputSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Если текущий пользователь - студент, он записывает сам себя
    target_student_id = (
        current_user.id if current_user.role == UserRoleChoices.student else (enrollment.student_id or current_user.id)
    )

    group = db.query(StudyGroup).filter(StudyGroup.id == enrollment.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    # Проверка статуса группы: должен быть recruiting
    if group.status != StudyGroupStatusChoices.recruiting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Набор в группу закрыт. Статус группы: '{group.status.value}'",
        )

    # Проверка вместимости группы (capacity)
    current_count = (
        db.query(Enrollment)
        .filter(
            Enrollment.group_id == group.id,
            Enrollment.status == EnrollmentStatusChoices.active,
        )
        .count()
    )
    if current_count >= group.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Лимит мест в группе исчерпан ({current_count}/{group.capacity})",
        )

    # Проверка на дубликат записи
    existing = (
        db.query(Enrollment)
        .filter(
            Enrollment.group_id == group.id,
            Enrollment.student_id == target_student_id,
            Enrollment.status == EnrollmentStatusChoices.active,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Студент уже записан в эту группу")

    enrollment_db = Enrollment(
        student_id=target_student_id,
        group_id=group.id,
        status=enrollment.status,
    )
    db.add(enrollment_db)
    db.commit()
    db.refresh(enrollment_db)
    return enrollment_db


@enrollment_router.get("/", response_model=List[EnrollmentOutSchema])
async def list_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    get_queryset:
    - Студент видит ТОЛЬКО свои записи на курсы/группы.
    - Менеджеры, преподаватели и администраторы видят полный список.
    """
    if current_user.role == UserRoleChoices.student:
        return db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()

    return db.query(Enrollment).all()


@enrollment_router.get("/{enrollment_id}/", response_model=EnrollmentOutSchema)
async def detail_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Enrollment).filter(Enrollment.id == enrollment_id)
    if current_user.role == UserRoleChoices.student:
        query = query.filter(Enrollment.student_id == current_user.id)

    enrollment_db = query.first()
    if not enrollment_db:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return enrollment_db


@enrollment_router.put("/{enrollment_id}/", response_model=dict)
async def update_enrollment(
    enrollment_id: int,
    enrollment: EnrollmentUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Enrollment).filter(Enrollment.id == enrollment_id)
    if current_user.role == UserRoleChoices.student:
        query = query.filter(Enrollment.student_id == current_user.id)

    enrollment_db = query.first()
    if not enrollment_db:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    update_data = enrollment.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(enrollment_db, key, value)

    db.commit()
    db.refresh(enrollment_db)
    return {"message": "Запись изменена"}


@enrollment_router.delete("/{enrollment_id}/", response_model=dict)
async def delete_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Enrollment).filter(Enrollment.id == enrollment_id)
    if current_user.role == UserRoleChoices.student:
        query = query.filter(Enrollment.student_id == current_user.id)

    enrollment_db = query.first()
    if not enrollment_db:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    db.delete(enrollment_db)
    db.commit()
    return {"message": "Запись удалена"}
