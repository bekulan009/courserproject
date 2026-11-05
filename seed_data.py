import sys
from pathlib import Path

# Добавляем корневую папку в sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from mysite.database.db import Base, engine, SessionLocal
from mysite.database.models import (
    User,
    Category,
    Course,
    StudyGroup,
    UserRoleChoices,
    UserStatusChoices,
    CourseLevelChoices,
    CourseStatusChoices,
    StudyGroupStatusChoices,
)
from mysite.auth import hash_password
from datetime import date, timedelta


def seed():
    # Создаем таблицы, если еще не созданы
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("[*] Nachinaem napolnenie bazy dannyh...")

    # 1. Создание тестовых пользователей для каждой роли
    users_data = [
        {
            "full_name": "Glavny Administrator",
            "email": "admin@example.com",
            "password": hash_password("admin123"),
            "role": UserRoleChoices.admin,
            "user_status": UserStatusChoices.pro,
            "is_active": True,
        },
        {
            "full_name": "Ivan Uchitel",
            "email": "teacher@example.com",
            "password": hash_password("teacher123"),
            "role": UserRoleChoices.teacher,
            "user_status": UserStatusChoices.pro,
            "is_active": True,
        },
        {
            "full_name": "Anna Menedzher",
            "email": "manager@example.com",
            "password": hash_password("manager123"),
            "role": UserRoleChoices.manager,
            "user_status": UserStatusChoices.pro,
            "is_active": True,
        },
        {
            "full_name": "Alexey Student (Pro)",
            "email": "student_active@example.com",
            "password": hash_password("student123"),
            "role": UserRoleChoices.student,
            "user_status": UserStatusChoices.pro,
            "is_active": True,
        },
        {
            "full_name": "Maria Student (Free)",
            "email": "student_free@example.com",
            "password": hash_password("student123"),
            "role": UserRoleChoices.student,
            "user_status": UserStatusChoices.free,
            "is_active": False,
        },
    ]

    created_users = {}
    for u in users_data:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            user_obj = User(**u)
            db.add(user_obj)
            db.commit()
            db.refresh(user_obj)
            created_users[u["email"]] = user_obj
            print(f"[+] User sozdal: {user_obj.full_name} ({user_obj.email}) [{user_obj.role.value}]")
        else:
            created_users[u["email"]] = existing

    # 2. Создание категорий
    categories_names = [
        "Backend Разработка",
        "Frontend Разработка",
        "Data Science & AI",
        "Основы программирования",
    ]
    created_categories = {}
    for cat_name in categories_names:
        cat_obj = db.query(Category).filter(Category.category_name == cat_name).first()
        if not cat_obj:
            cat_obj = Category(category_name=cat_name)
            db.add(cat_obj)
            db.commit()
            db.refresh(cat_obj)
            print(f"[+] Category sozdana: {cat_name}")
        created_categories[cat_name] = cat_obj

    # 3. Создание 5 курсов
    courses_data = [
        {
            "title": "Основы Python для начинающих",
            "category_id": created_categories["Основы программирования"].id,
            "description": "Вводный курс в программирование на Python с нуля: синтаксис, переменные, циклы, функции и базовые структуры данных.",
            "level": CourseLevelChoices.beginner,
            "price": 0.0,
            "duration_weeks": 4,
            "is_active": True,
            "status": CourseStatusChoices.free,
        },
        {
            "title": "FastAPI и SQLAlchemy: Бэкенд на Python",
            "category_id": created_categories["Backend Разработка"].id,
            "description": "Полный практический курс по созданию современных REST API: асинхронность, базы данных, Pydantic, авторизация по токенам и развертывание.",
            "level": CourseLevelChoices.intermediate,
            "price": 18000.0,
            "duration_weeks": 8,
            "is_active": True,
            "status": CourseStatusChoices.plus,
        },
        {
            "title": "Современный Frontend на React & TypeScript",
            "category_id": created_categories["Frontend Разработка"].id,
            "description": "Разработка клиентских интерфейсов: компоненты, хуки, типизация TypeScript, работа со стейтом Redux Toolkit и роутингом.",
            "level": CourseLevelChoices.intermediate,
            "price": 16000.0,
            "duration_weeks": 10,
            "is_active": True,
            "status": CourseStatusChoices.plus,
        },
        {
            "title": "Data Science и Машинное обучение",
            "category_id": created_categories["Data Science & AI"].id,
            "description": "Продвинутый курс по анализу данных: NumPy, Pandas, визуализация данных, Scikit-Learn и построение прогнозных ML-моделей.",
            "level": CourseLevelChoices.advanced,
            "price": 24000.0,
            "duration_weeks": 12,
            "is_active": True,
            "status": CourseStatusChoices.plus,
        },
        {
            "title": "Базы данных и основы SQL",
            "category_id": created_categories["Backend Разработка"].id,
            "description": "Бесплатный практический интенсив: проектирование реляционных баз данных, сложные SQL-запросы, JOIN, группировки и индексы.",
            "level": CourseLevelChoices.beginner,
            "price": 0.0,
            "duration_weeks": 3,
            "is_active": True,
            "status": CourseStatusChoices.free,
        },
    ]

    for c in courses_data:
        existing_course = db.query(Course).filter(Course.title == c["title"]).first()
        if not existing_course:
            course_obj = Course(**c)
            db.add(course_obj)
            db.commit()
            db.refresh(course_obj)
            print(f"[+] Kurs sozdan: '{course_obj.title}' (uroven: {course_obj.level.value}, status: {course_obj.status.value}, cena: {course_obj.price})")
        else:
            print(f"[*] Kurs uzhe sushestvuet: '{existing_course.title}'")

    # 4. Создание учебной группы для первого курса
    teacher = created_users.get("teacher@example.com")
    first_course = db.query(Course).first()
    if teacher and first_course:
        existing_group = db.query(StudyGroup).filter(StudyGroup.name == "Группа PY-101 (Набор открыт)").first()
        if not existing_group:
            group = StudyGroup(
                name="Группа PY-101 (Набор открыт)",
                course_id=first_course.id,
                teacher_id=teacher.id,
                starts_on=date.today() + timedelta(days=7),
                ends_on=date.today() + timedelta(days=35),
                capacity=15,
                status=StudyGroupStatusChoices.recruiting,
            )
            db.add(group)
            db.commit()
            print(f"[+] Uchebnaya gruppa sozdana: '{group.name}' (capacity: {group.capacity}, status: recruiting)")

    db.close()
    print("[OK] Baza dannyh uspeshno zapolnena 5 kursami i polzovatelyami!")


if __name__ == "__main__":
    seed()
