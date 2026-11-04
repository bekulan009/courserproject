# Course Management System (FastAPI Backend)

Бэкенд-проект на FastAPI и SQLAlchemy для платформы онлайн-курсов и управления учебным процессом.

## 🚀 Структура проекта

```text
Course-Project/
├── mysite/
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── reviews.py        # Представления SQLAdmin для моделей
│   │   └── setup.py          # Настройка и регистрация админки
│   ├── api/
│   │   ├── __init__.py
│   │   ├── users.py          # CRUD для пользователей (User)
│   │   ├── categories.py     # CRUD для категорий (Category)
│   │   ├── courses.py        # CRUD для курсов (Course)
│   │   ├── study_groups.py   # CRUD для учебных групп (StudyGroup)
│   │   ├── applications.py   # CRUD для заявок (Application)
│   │   └── enrollments.py    # CRUD для зачислений (Enrollment)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py             # Подключение к SQLite, сессии и Base
│   │   ├── models.py         # SQLAlchemy модели данных
│   │   └── schemas.py        # Pydantic схемы валидации
│   ├── config.py             # Конфигурация и переменные окружения
│   └── __init__.py
├── .env                      # Переменные окружения
├── .gitignore
├── requirements.txt          # Зависимости проекта
├── main.py                   # Точка входа приложения
└── course.db                 # База данных SQLite (создается автоматически)
```

## 📋 Модели данных

1. **User**
   - `id`: Уникальный идентификатор
   - `full_name`: Полное имя
   - `email`: Уникальный email
   - `password`: Пароль
   - `role`: Роль (`student`, `teacher`, `manager`, `admin`)
   - `user_status`: Статус пользователя (`free`, `pro`)
   - `created_at`: Дата и время создания
   - `updated_at`: Дата и время обновления

2. **Category**
   - `id`: Идентификатор
   - `category_name`: Название категории (уникальное)

3. **Course**
   - `id`: Идентификатор
   - `title`: Название курса
   - `category_id`: Внешний ключ на категорию
   - `description`: Описание курса
   - `level`: Уровень сложности (`beginner`, `intermediate`, `advanced`)
   - `price`: Стоимость курса
   - `duration_weeks`: Продолжительность в неделях
   - `is_active`: Флаг активности
   - `status`: Статус курса (`free`, `plus`)
   - `created_at`: Дата и время создания
   - `updated_at`: Дата и время обновления

4. **StudyGroup**
   - `id`: Идентификатор
   - `name`: Название группы
   - `course_id`: Внешний ключ на курс
   - `teacher_id`: Внешний ключ на преподавателя (`User`)
   - `starts_on`: Дата начала занятий
   - `ends_on`: Дата окончания занятий
   - `status`: Статус группы (`recruiting`, `active`, `completed`, `cancelled`)
   - `created_at`: Дата и время создания
   - `updated_at`: Дата и время обновления

5. **Application**
   - `id`: Идентификатор
   - `student_id`: Внешний ключ на студента (`User`)
   - `course_id`: Внешний ключ на курс (`Course`)
   - `manager_id`: Внешний ключ на менеджера (`User`, опционально)
   - `comment`: Комментарий к заявке
   - `status`: Статус заявки (`new`, `in_progress`, `accepted`, `rejected`, `cancelled`)
   - `created_at`: Дата и время создания
   - `updated_at`: Дата и время обновления

6. **Enrollment**
   - `id`: Идентификатор
   - `student_id`: Внешний ключ на студента (`User`)
   - `group_id`: Внешний ключ на группу (`StudyGroup`)
   - `status`: Статус записи (`active`, `completed`, `cancelled`)
   - `created_at`: Дата и время записи

## 🛠 Запуск проекта

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите сервер:
```bash
python main.py
```
или:
```bash
uvicorn main:app --reload
```

3. Откройте в браузере:
- **Swagger UI (Интерактивная документация API)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **SQLAdmin Панель управления**: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
