# TaskFlow API v2

**TaskFlow API** — бэкенд-сервис для управления задачами, проектами и пользователями.  
Проект разработан в рамках учебного плана. На текущем этапе реализовано:

- Хранение данных в **PostgreSQL** с использованием SQLAlchemy ORM и Alembic для миграций.
- **S3-совместимое хранилище (MinIO)** для загрузки и хранения файлов, прикреплённых к задачам.
- **Аутентификация и авторизация через Keycloak** (JWT-токены, роли `user` и `admin`).
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
- **Keycloak** – сервер аутентификации (OpenID Connect)
- **python-keycloak** / **python-jose** – работа с JWT и Keycloak
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
│   │   ├── enums.py
│   │   └── security.py
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
| **Security**  | Проверка JWT-токенов, получение текущего пользователя из Keycloak.       |

Все эндпоинты (кроме `POST /users` и корневого) защищены и требуют валидный JWT-токен.  
Полная документация API генерируется автоматически и доступна по адресу `/docs`.

---

## Аутентификация и авторизация (Keycloak)

**Keycloak** используется как центральный сервер аутентификации.  
- Все защищённые эндпоинты ожидают заголовок `Authorization: Bearer <token>`.
- Токен проверяется через JWKS (публичные ключи Keycloak).
- Пользователи синхронизируются с локальной таблицей `users` автоматически при первом обращении (по `preferred_username` из токена).

### Роли и права доступа

| Роль    | Права                                                                 |
|---------|-----------------------------------------------------------------------|
| **user** | - Создаёт свои задачи и проекты<br>- Редактирует и удаляет только свои ресурсы<br>- Загружает и скачивает файлы только к своим задачам |
| **admin** | - Просматривает все задачи, проекты, пользователей<br>- Удаляет любые задачи и проекты<br>- Управляет пользователями (просмотр, обновление, удаление) |

### Настройка Keycloak

Перед запуском приложения необходимо создать realm и клиента в Keycloak:

1. Зайдите в админ-консоль `http://localhost:8080` (логин/пароль заданы в `.env`).
2. Создайте realm `taskflow`.
3. Создайте клиента `taskflow-api` с включённой аутентификацией (Client authentication).
4. Скопируйте **Client Secret** из вкладки Credentials.
5. Добавьте роли `user` и `admin` (Realm roles).
6. Создайте тестовых пользователей и назначьте им роли.

Подробная инструкция описана в документации проекта.

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

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=taskflow
KEYCLOAK_CLIENT_ID=taskflow-api
KEYCLOAK_CLIENT_SECRET=your-client-secret 
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

> **Примечание:** Все эндпоинты, кроме `POST /users` и корневого (`/`), защищены и требуют валидный JWT-токен (заголовок `Authorization: Bearer <token>`).  
> Пользователь с ролью `user` видит и управляет только своими ресурсами.  
> Пользователь с ролью `admin` имеет полный доступ ко всем ресурсам.

---

### Задачи (`/tasks`)

| Метод   | Эндпоинт                   | Описание                                                                 |
|---------|----------------------------|--------------------------------------------------------------------------|
| `GET`   | `/tasks`                   | Список задач (фильтрация, пагинация). user видит только свои, admin – все. |
| `POST`  | `/tasks`                   | Создать задачу (автор подставляется из токена).                          |
| `GET`   | `/tasks/{task_id}`         | Получить задачу по ID (только свою или admin).                           |
| `PATCH` | `/tasks/{task_id}`         | Частично обновить задачу (только свою или admin).                        |
| `DELETE`| `/tasks/{task_id}`         | Удалить задачу (только свою или admin).                                  |

---

### Проекты (`/projects`)

| Метод   | Эндпоинт                     | Описание                                                                 |
|---------|------------------------------|--------------------------------------------------------------------------|
| `GET`   | `/projects`                  | Список проектов (user – свои, admin – все).                              |
| `POST`  | `/projects`                  | Создать проект (владелец подставляется из токена).                       |
| `GET`   | `/projects/{project_id}`     | Получить проект по ID (только свой или admin).                           |
| `PATCH` | `/projects/{project_id}`     | Обновить проект (только свой или admin).                                 |
| `DELETE`| `/projects/{project_id}`     | Удалить проект (только свой или admin; если есть задачи – конфликт).     |

---

### Пользователи (`/users`)

| Метод   | Эндпоинт             | Описание                                                                 |
|---------|----------------------|--------------------------------------------------------------------------|
| `POST`  | `/users`             | **Открытый** эндпоинт – регистрация нового пользователя в БД.            |
| `GET`   | `/users`             | Список всех пользователей (только для admin).                            |
| `GET`   | `/users/{user_id}`   | Получить пользователя по ID (только себя или admin).                     |
| `PATCH` | `/users/{user_id}`   | Обновить пользователя (только себя или admin).                           |
| `DELETE`| `/users/{user_id}`   | Удалить пользователя (только для admin).                                 |

---

### Вложения (файлы) (`/tasks/{task_id}/attachments`)

| Метод   | Эндпоинт                                                      | Описание                                                                 |
|---------|---------------------------------------------------------------|--------------------------------------------------------------------------|
| `POST`  | `/tasks/{task_id}/attachments`                                | Загрузить файл к задаче (multipart/form-data). Только автор или admin.   |
| `GET`   | `/tasks/{task_id}/attachments`                                | Получить список файлов задачи (только автор или admin).                  |
| `GET`   | `/tasks/{task_id}/attachments/{attachment_id}/download`       | Получить временную ссылку на скачивание (presigned URL). Только автор или admin. |
| `DELETE`| `/tasks/{task_id}/attachments/{attachment_id}`                | Удалить файл (из S3 и БД). Только автор или admin. 
