# TaskFlow API v2

**TaskFlow API** — бэкенд-сервис для управления задачами, проектами и пользователями.  
Проект разработан в рамках учебного плана. На текущем этапе реализовано:

- Хранение данных в **PostgreSQL** с использованием SQLAlchemy ORM и Alembic для миграций.
- **S3-совместимое хранилище (MinIO)** для загрузки и хранения файлов, прикреплённых к задачам.
- API документировано через Swagger (OpenAPI).

---

## Стек технологий

- **Python** 3.12
- **FastAPI** – веб-фреймворк
- **Pydantic** – валидация данных и схемы
- **Uvicorn** – ASGI-сервер
- **SQLAlchemy** 2.0 – ORM
- **Alembic** – миграции базы данных
- **asyncpg** / **psycopg2** – драйверы PostgreSQL
- **aiobotocore** – асинхронный клиент для S3
- **python-multipart** – обработка загрузки файлов
- **MinIO** – S3-совместимое хранилище (для локальной разработки)
- **Docker** и **Docker Compose** – контейнеризация
- **OpenAPI / Swagger** – автодокументация API

---

## Структура проекта

```text
TaskFlow_API_v2/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── tasks.py
│   │       │   ├── projects.py
│   │       │   ├── users.py
│   │       │   └── attachments.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   └── enums.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models/
│   │       ├── task.py
│   │       ├── project.py
│   │       ├── user.py
│   │       └── attachment.py
│   ├── repositories/
│   │   ├── task_repository.py
│   │   ├── project_repository.py
│   │   ├── user_repository.py
│   │   └── attachment_repository.py
│   ├── schemas/
│   │   ├── task.py
│   │   ├── project.py
│   │   ├── user.py
│   │   └── attachment.py
│   ├── services/
│   │   ├── task_service.py
│   │   ├── project_service.py
│   │   ├── user_service.py
│   │   └── attachment_service.py
│   ├── storage/
│   │   └── s3_client.py
│   └── main.py
├── alembic/
│   ├── versions/
│   └── env.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Модули и слои

| Слой          | Описание                                                                 |
|---------------|--------------------------------------------------------------------------|
| **API (endpoints)** | Обрабатывают HTTP-запросы, валидируют входные данные через Pydantic, вызывают сервисы. |
| **Services**  | Содержат бизнес-логику: проверки существования связанных сущностей, загрузка/удаление файлов в S3, генерация ссылок. |
| **Repositories** | Инкапсулируют запросы к базе данных через SQLAlchemy.                     |
| **Models**    | SQLAlchemy-модели, описывающие таблицы БД.                               |
| **Schemas**   | Pydantic-схемы для валидации запросов и сериализации ответов.            |
| **Storage**   | Клиент для работы с S3-совместимым хранилищем (MinIO).                   |

Все эндпоинты доступны по префиксу `/api/v1`.  
Полная документация API генерируется автоматически и доступна по адресу `/docs`.

---

## База данных и миграции

Проект использует **PostgreSQL** как основное хранилище.  
Управление схемой выполняется через **Alembic**.

### Модели данных

- **User** – пользователи (username, email, full_name, is_active, created_at)
- **Project** – проекты (title, description, owner_id, created_at)
- **Task** – задачи (title, description, status, deadline, project_id, assignee_id, priority, user_id, created_at)
- **Attachment** – вложения (task_id, file_name, file_key, content_type, size, bucket_name, created_at, uploaded_by_user_id)

Связи:  
- Проект → Задачи (один ко многим)
- Пользователь → Задачи (как исполнитель и как автор)
- Пользователь → Проекты (как владелец)
- Задача → Вложения (один ко многим)
- Пользователь → Вложения (как загрузивший)

### Команды для миграций

Все команды выполняются внутри контейнера `app`:

```bash
# Создать миграцию на основе изменений в моделях
docker-compose exec app alembic revision --autogenerate -m "Описание изменений"

# Применить все миграции
docker-compose exec app alembic upgrade head

# Откатить последнюю миграцию
docker-compose exec app alembic downgrade -1
```

Если база данных пуста, миграции создадут все необходимые таблицы.

---

## S3-хранилище (MinIO)

Для хранения файлов используется **MinIO** – S3-совместимое хранилище.  
При запуске через Docker Compose автоматически создаётся bucket `taskflow-files` (с помощью сервиса `minio-init`).

**Доступ к консоли MinIO:**  
- Адрес: `http://localhost:9001`  
- Логин: `minioadmin`  
- Пароль: `minioadmin`

**Проверка загруженных файлов:**  
Зайдите в консоль, выберите bucket `taskflow-files` – там будут все загруженные через API файлы.

---

## Переменные окружения

Для работы приложения требуется файл `.env` (пример в `.env.example`):

```env
# Режим работы
ENV=development

# Строка подключения к PostgreSQL
DATABASE_URL=postgresql://user:password@host:port/dbname

# MinIO / S3
MINIO_HOST=minio
MINIO_PORT=9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=taskflow-files
MINIO_SECURE=False
```

В Docker Compose переменные загружаются автоматически из `.env` файла.

---

## Запуск проекта

### Локальный запуск (без Docker)

1. Убедитесь, что установлен Python 3.12 и PostgreSQL (или используйте удалённую БД).
2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Создайте файл `.env` со строкой подключения к вашей БД.
5. Примените миграции:
   ```bash
   alembic upgrade head
   ```
6. Запустите сервер:
   ```bash
   uvicorn app.main:app --reload
   ```
7. Откройте Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Запуск через Docker Compose (рекомендованный способ)

1. Убедитесь, что Docker и Docker Compose установлены.
2. В корневой папке проекта выполните:
   ```bash
   docker-compose up --build
   ```
3. Дождитесь запуска контейнеров (`app` и `postgres`).
4. Примените миграции (если они не применяются автоматически):
   ```bash
   docker-compose exec app alembic upgrade head
   ```
5. Приложение доступно по адресу: [http://localhost:8000](http://localhost:8000)  
   Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

6. Для остановки нажмите `Ctrl+C`, затем:
   ```bash
   docker-compose down
   ```
   Чтобы полностью удалить данные БД (том), используйте `docker-compose down -v`.

---

## Доступные эндпоинты (кратко)

### Задачи (`/tasks`)

- `GET    /tasks` – список задач с фильтрацией по статусу, проекту, приоритету, исполнителю и пагинацией (параметры: `status`, `project_id`, `priority`, `assignee_id`, `limit`, `offset`)
- `POST   /tasks` – создать задачу
- `GET    /tasks/{task_id}` – получить задачу по ID
- `PATCH  /tasks/{task_id}` – частично обновить задачу
- `DELETE /tasks/{task_id}` – удалить задачу

### Проекты (`/projects`)

- `GET    /projects` – список всех проектов
- `POST   /projects` – создать проект
- `GET    /projects/{project_id}` – получить проект по ID
- `PATCH  /projects/{project_id}` – обновить проект
- `DELETE /projects/{project_id}` – удалить проект

### Пользователи (`/users`)

- `GET    /users` – список всех пользователей
- `POST   /users` – создать пользователя
- `GET    /users/{user_id}` – получить пользователя по ID
- `PATCH  /users/{user_id}` – обновить пользователя
- `DELETE /users/{user_id}` – удалить пользователя

### Вложения (файлы) (/tasks/{task_id}/attachments)

- `POST /tasks/{task_id}/attachments` – загрузить файл к задаче (multipart/form-data)
- `GET /tasks/{task_id}/attachments` – получить список файлов задачи
- `GET /tasks/{task_id}/attachments/{attachment_id}/download` – получить временную ссылку на скачивание (presigned URL)
- `DELETE /tasks/{task_id}/attachments/{attachment_id}` – удалить файл (из S3 и БД)
