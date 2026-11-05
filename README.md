# Course Management System (FastAPI Backend)

Комплексный бэкенд на FastAPI и SQLAlchemy для образовательной платформы с ролевой моделью доступа (JWT), AI-поиском курсов и админ-панелью.

---

## 🚀 Структура проекта

```text
Course-Project/
├── mysite/
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── reviews.py             # Представления SQLAdmin для моделей
│   │   └── setup.py               # Настройка и подключение админки
│   ├── api/
│   │   ├── __init__.py
│   │   ├── users.py               # Регистрация, логин (JWT), профиль, пользователи
│   │   ├── categories.py          # Category CRUD (доступ только ADMIN)
│   │   ├── courses.py             # Course CRUD (доступ только TEACHER)
│   │   ├── applications.py        # Application Create (STUDENT) & Управление (MANAGER)
│   │   ├── study_groups.py        # StudyGroup CRUD & запись (recruiting, capacity)
│   │   ├── enrollments.py         # Enrollment (get_queryset для студента)
│   │   └── ai.py                  # AI Assistant (/ai/search)
│   ├── base_knowledge/
│   │   └── __init__.py            # База знаний образовательных направлений
│   ├── chains/
│   │   ├── __init__.py
│   │   └── ai_search.py           # LangChain + Ollama цепочка AI-поиска курсов
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py                  # Подключение к SQLite, Base, get_db
│   │   ├── models.py              # Модели SQLAlchemy
│   │   └── schemas.py             # Схемы валидации Pydantic
│   ├── auth.py                    # JWT токены, хеширование паролей (bcrypt), зависимости ролей
│   ├── config.py                  # Конфигурация, секреты, время жизни токенов
│   └── __init__.py
├── .env                           # Переменные окружения
├── requirements.txt               # Зависимости
├── main.py                        # Точка входа приложения
└── course.db                      # SQLite база данных
```

---

## 🔐 Ролевая модель доступа и права (Permissions)

| Модель / Сущность | Действие | Разрешенная роль | Особенности и бизнес-логика |
|---|---|---|---|
| **Category** | Create, Read, Update, Delete | **ADMIN** | Полный CRUD доступен только администраторам. |
| **Course** | Create, Update, Delete | **TEACHER** (или ADMIN) | Преподаватель управляет своими курсами. |
| **Application** | Create | **STUDENT** | • `student.is_active == True` — может подать заявку на любой курс.<br>• `student.is_active == False` — разрешено **только** на бесплатные курсы (`course.status == 'free'`). |
| **Application** | List, Detail, Update, Delete | **MANAGER** (или ADMIN) | Менеджер обрабатывает заявки, меняет статус, оставляет комментарии. |
| **Enrollment** | List (`get_queryset`) | **STUDENT** | Студент видит **только свои** записи на обучение (`student_id == current_user.id`). Менеджеры и админы видят все. |
| **StudyGroup** | Join / Create Enrollment | **STUDENT** | • Проверка статуса группы: только `recruiting`.<br>• Проверка лимита: текущее число активных записей `< capacity`. |

---

## 🔑 Аутентификация через JWT Токены

1. **Регистрация**: `POST /user/register/` (принимает `full_name`, `email`, `password`, `role`, `user_status`).
2. **Логин**: `POST /user/login/` (возвращает `access_token`, `refresh_token`, `token_type: "bearer"`).
3. **Swagger UI Авторизация**: `POST /user/login-token` — позволяет использовать стандартную зеленую кнопку **Authorize** в правом верхнем углу Swagger UI.
4. **Профиль текущего пользователя**: `GET /user/me/` (требует Bearer токен).

---

## 🤖 AI Search (`/ai/search`)

В модуле `mysite/chains/ai_search.py` реализована LangChain-цепочка:
- Использует модель Ollama (`llama3.2`) и структурированный вывод (`AISearchOutputSchema`).
- Использует базу знаний из `mysite/base_knowledge/`.
- Системный промпт анализирует запрос пользователя, уровень подготовки и подбирает список рекомендованных программ с объяснением причин выбора.
- При отсутствии запущенного сервиса Ollama автоматически срабатывает fallback-поиск по локальной базе данных курсов.

---

## ⚙️ Запуск и работа

```powershell
cd C:\Users\User\.gemini\antigravity\scratch\Course-Project
python main.py
```

- 📖 **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ⚙️ **SQLAdmin Панель**: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
