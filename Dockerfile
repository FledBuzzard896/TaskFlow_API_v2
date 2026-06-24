# Образ с Python 3.12-slim
FROM python:3.12-slim

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копирование файла с зависимостями в контейнер
COPY requirements.txt .

# Установка зависимости (--no-cache-dir экономит место)
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта в контейнер (кроме того, что исключено в .dockerignore)
COPY . .

# Команда дял запуска приложения при старте контейнера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
