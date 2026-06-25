# TaskFlow API v2

**TaskFlow API** — это бэкенд-сервис для управления задачами, проектами и пользователями.  
Проект разработан в рамках учебного плана и представляет собой REST API с открытой документацией (Swagger).  
На текущем этапе данные хранятся в оперативной памяти, но структура готова к масштабированию и подключению внешних сервисов (PostgreSQL, S3, Keycloak).

---

## Стек технологий

- **Python** 3.12
- **FastAPI** – веб-фреймворк
- **Pydantic** – валидация данных и схемы
- **Uvicorn** – ASGI-сервер
- **Docker** и **Docker Compose** – контейнеризация
- **OpenAPI / Swagger** – автодокументация API

---

## Структура проекта
```text
TaskFlow_API_v2/
├── app/
│ ├── api/
│ │ └── v1/
│ │ ├── endpoints/
│ │ │ ├── tasks.py
│ │ │ ├── projects.py
│ │ │ └── users.py
│ │ └── router.py
│ ├── core/
│ │ └── config.py 
│ ├── schemas/
│ │ ├── tasks.py
│ │ ├── projects.py
│ │ └── users.py
│ └── main.py 
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Модули API

| Модуль        | Описание                                                                 |
|---------------|--------------------------------------------------------------------------|
| **Tasks**     | Управление задачами: создание, просмотр (с фильтрацией и пагинацией), обновление, удаление. |
| **Projects**  | Управление проектами: создание, просмотр, обновление, удаление.           |
| **Users**     | Управление пользователями: создание, просмотр, обновление, удаление.      |

Все эндпоинты доступны по префиксу `/api/v1`.  
Полная документация автоматически генерируется и доступна по адресу `/docs`.

---

## Переменные окружения

Для работы приложения используется файл `.env` (или переменные окружения).  
Пример доступен в `.env.example`:

```env
# Режим работы приложения
ENV=development
```
## Запуск проекта

### Локальный запуск (без Docker)

1. Убедитесь, что установлен Python 3.12.
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

4. Запустите сервер:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Откройте в браузере: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Запуск через Docker Compose (рекомендованный способ)

1. Убедитесь, что Docker и Docker Compose установлены.
2. В корневой папке проекта выполните:

   ```bash
   docker-compose up --build
   ```

3. Приложение будет доступно по адресу: [http://localhost:8000](http://localhost:8000)  
   Swagger-документация: [http://localhost:8000/docs](http://localhost:8000/docs)

4. Для остановки нажмите `Ctrl+C`, затем выполните:

   ```bash
   docker-compose down
   ```

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
