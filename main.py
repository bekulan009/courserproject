from fastapi import FastAPI
import uvicorn

from mysite.api import (
    user_router,
    category_router,
    course_router,
    study_group_router,
    application_router,
    enrollment_router,
    ai_router,
)
from mysite.database.db import Base, engine
from mysite.admin.setup import setup_admin

# Создание таблиц базы данных
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Course Management System",
    description="REST API для управления курсами, пользователями, группами, заявками и AI консультантом",
    version="1.1.0",
)

# Подключение маршрутов
app.include_router(user_router)
app.include_router(category_router)
app.include_router(course_router)
app.include_router(study_group_router)
app.include_router(application_router)
app.include_router(enrollment_router)
app.include_router(ai_router)

# Подключение админ-панели (доступна по адресу /admin)
setup_admin(app)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
