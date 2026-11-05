from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .db import Base


class UserRoleChoices(str, PyEnum):
    student = "student"
    teacher = "teacher"
    manager = "manager"
    admin = "admin"


class UserStatusChoices(str, PyEnum):
    free = "free"
    pro = "pro"


class CourseLevelChoices(str, PyEnum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class CourseStatusChoices(str, PyEnum):
    free = "free"
    plus = "plus"


class StudyGroupStatusChoices(str, PyEnum):
    recruiting = "recruiting"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class ApplicationStatusChoices(str, PyEnum):
    new = "new"
    in_progress = "in_progress"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"


class EnrollmentStatusChoices(str, PyEnum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRoleChoices), default=UserRoleChoices.student, nullable=False)
    user_status = Column(SQLEnum(UserStatusChoices), default=UserStatusChoices.free, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    teaching_groups = relationship("StudyGroup", back_populates="teacher", foreign_keys="StudyGroup.teacher_id")
    student_applications = relationship("Application", back_populates="student", foreign_keys="Application.student_id")
    manager_applications = relationship("Application", back_populates="manager", foreign_keys="Application.manager_id")
    enrollments = relationship("Enrollment", back_populates="student")

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), unique=True, nullable=False)

    courses = relationship("Course", back_populates="category")

    def __str__(self):
        return self.category_name


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(SQLEnum(CourseLevelChoices), default=CourseLevelChoices.beginner, nullable=False)
    price = Column(Float, default=0.0, nullable=False)
    duration_weeks = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(SQLEnum(CourseStatusChoices), default=CourseStatusChoices.free, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    category = relationship("Category", back_populates="courses")
    study_groups = relationship("StudyGroup", back_populates="course")
    applications = relationship("Application", back_populates="course")

    def __str__(self):
        return self.title


class StudyGroup(Base):
    __tablename__ = "study_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    starts_on = Column(Date, nullable=False)
    ends_on = Column(Date, nullable=True)
    capacity = Column(Integer, default=20, nullable=False)
    status = Column(SQLEnum(StudyGroupStatusChoices), default=StudyGroupStatusChoices.recruiting, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    course = relationship("Course", back_populates="study_groups")
    teacher = relationship("User", back_populates="teaching_groups", foreign_keys=[teacher_id])
    enrollments = relationship("Enrollment", back_populates="group")

    def __str__(self):
        return self.name


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    comment = Column(Text, nullable=True)
    status = Column(SQLEnum(ApplicationStatusChoices), default=ApplicationStatusChoices.new, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    student = relationship("User", back_populates="student_applications", foreign_keys=[student_id])
    course = relationship("Course", back_populates="applications")
    manager = relationship("User", back_populates="manager_applications", foreign_keys=[manager_id])

    def __str__(self):
        return f"Application #{self.id} (Student ID: {self.student_id})"


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("study_groups.id"), nullable=False)
    status = Column(SQLEnum(EnrollmentStatusChoices), default=EnrollmentStatusChoices.active, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    student = relationship("User", back_populates="enrollments", foreign_keys=[student_id])
    group = relationship("StudyGroup", back_populates="enrollments")

    def __str__(self):
        return f"Enrollment #{self.id} (Student ID: {self.student_id})"
