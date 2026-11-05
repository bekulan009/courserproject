from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime, date
from typing import Optional, List
from .models import (
    UserRoleChoices,
    UserStatusChoices,
    CourseLevelChoices,
    CourseStatusChoices,
    StudyGroupStatusChoices,
    ApplicationStatusChoices,
    EnrollmentStatusChoices,
)


# ================== Token & Auth Schemas ==================
class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenDataSchema(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserRegisterSchema(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRoleChoices = UserRoleChoices.student
    user_status: UserStatusChoices = UserStatusChoices.free


# ================== User Schemas ==================
class UserInputSchema(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRoleChoices = UserRoleChoices.student
    user_status: UserStatusChoices = UserStatusChoices.free
    is_active: bool = True


class UserUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRoleChoices] = None
    user_status: Optional[UserStatusChoices] = None
    is_active: Optional[bool] = None


class UserOutSchema(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRoleChoices
    user_status: UserStatusChoices
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ================== Category Schemas ==================
class CategoryInputSchema(BaseModel):
    category_name: str


class CategoryUpdateSchema(BaseModel):
    category_name: Optional[str] = None


class CategoryOutSchema(BaseModel):
    id: int
    category_name: str

    model_config = ConfigDict(from_attributes=True)


# ================== Course Schemas ==================
class CourseInputSchema(BaseModel):
    title: str
    category_id: int
    description: Optional[str] = None
    level: CourseLevelChoices = CourseLevelChoices.beginner
    price: float = 0.0
    duration_weeks: int = 1
    is_active: bool = True
    status: CourseStatusChoices = CourseStatusChoices.free


class CourseUpdateSchema(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    level: Optional[CourseLevelChoices] = None
    price: Optional[float] = None
    duration_weeks: Optional[int] = None
    is_active: Optional[bool] = None
    status: Optional[CourseStatusChoices] = None


class CourseOutSchema(BaseModel):
    id: int
    title: str
    category_id: int
    description: Optional[str] = None
    level: CourseLevelChoices
    price: float
    duration_weeks: int
    is_active: bool
    status: CourseStatusChoices
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ================== StudyGroup Schemas ==================
class StudyGroupInputSchema(BaseModel):
    name: str
    course_id: int
    teacher_id: int
    starts_on: date
    ends_on: Optional[date] = None
    capacity: int = 20
    status: StudyGroupStatusChoices = StudyGroupStatusChoices.recruiting


class StudyGroupUpdateSchema(BaseModel):
    name: Optional[str] = None
    course_id: Optional[int] = None
    teacher_id: Optional[int] = None
    starts_on: Optional[date] = None
    ends_on: Optional[date] = None
    capacity: Optional[int] = None
    status: Optional[StudyGroupStatusChoices] = None


class StudyGroupOutSchema(BaseModel):
    id: int
    name: str
    course_id: int
    teacher_id: int
    starts_on: date
    ends_on: Optional[date] = None
    capacity: int
    status: StudyGroupStatusChoices
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ================== Application Schemas ==================
class ApplicationInputSchema(BaseModel):
    course_id: int
    student_id: Optional[int] = None
    manager_id: Optional[int] = None
    comment: Optional[str] = None
    status: ApplicationStatusChoices = ApplicationStatusChoices.new


class ApplicationUpdateSchema(BaseModel):
    student_id: Optional[int] = None
    course_id: Optional[int] = None
    manager_id: Optional[int] = None
    comment: Optional[str] = None
    status: Optional[ApplicationStatusChoices] = None


class ApplicationOutSchema(BaseModel):
    id: int
    student_id: int
    course_id: int
    manager_id: Optional[int] = None
    comment: Optional[str] = None
    status: ApplicationStatusChoices
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ================== Enrollment Schemas ==================
class EnrollmentInputSchema(BaseModel):
    group_id: int
    student_id: Optional[int] = None
    status: EnrollmentStatusChoices = EnrollmentStatusChoices.active


class EnrollmentUpdateSchema(BaseModel):
    student_id: Optional[int] = None
    group_id: Optional[int] = None
    status: Optional[EnrollmentStatusChoices] = None


class EnrollmentOutSchema(BaseModel):
    id: int
    student_id: int
    group_id: int
    status: EnrollmentStatusChoices
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ================== AI Search Schemas ==================
class AISearchInputSchema(BaseModel):
    text: str = Field(..., description="Запрос пользователя о курсе, например: Хочу выучить бэкенд на Python с нуля")


class CourseRecommendationSchema(BaseModel):
    title: str
    category: str
    level: str
    price: float
    status: str
    reason: str


class AISearchOutputSchema(BaseModel):
    reply: str
    recommendations: List[CourseRecommendationSchema] = []
