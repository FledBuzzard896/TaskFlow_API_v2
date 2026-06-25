from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings


# Строим асинхронную строку подключения
async_db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Создаём асинхронный движок
engine = create_async_engine(
    async_db_url,
    echo=True,      # выводить SQL-запросы в консоль
    future=True,    # использовать новый стиль SQLAlchemy 2.0
)

# Создаём фабрику асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False, # не истекать после коммита (удобно для возврата данных)
)

# Функция-зависимость для получения сессии в эндпоинтах
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session