from typing import List
from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.users import UserResponse, UserCreate, UserUpdate
from app.services.user_service import UserService


router = APIRouter(
    tags=["users"],
)


@router.get("/users", response_model=List[UserResponse])
async def print_users(db: AsyncSession = Depends(get_db)):
    """
    Получить список всех пользователей.
    :return: Список пользователей
    """
    user_service = UserService(db)
    return await user_service.user_repo.get_all()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate,
                      db: AsyncSession = Depends(get_db)):
    """
    Создать нового пользователя.
    Проверка на уникальность username.
    :param data: Данные для создания пользователя
    :param db: Сессия подключения к БД
    :return: Созданный пользователь
    """
    user_service = UserService(db)
    return await user_service.create_user(data.model_dump())


@router.get("/users/{user_id}", response_model=UserResponse)
async def print_user(user_id: int,
                     db: AsyncSession = Depends(get_db)):
    """
    Получить пользователя по ID.
    :param user_id: ID пользователя
    :param db: Сессия подключения к БД
    :return: Найденный пользователь
    """
    user_service = UserService(db)
    return await user_service.get_by_id(user_id)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int,
                      update_data: UserUpdate,
                      db: AsyncSession = Depends(get_db)):
    """
    Частичное обновление пользователя.
    При смене username проверяет, что имя не занято другим пользователем.
    :param user_id: ID пользователя
    :param update_data: Обновляемые поля
    :param db: Сессия подключения к БД
    :return: Обновлённый пользователь
    """
    user_service = UserService(db)
    return await user_service.update_user(user_id, update_data.dict(exclude_unset=True))


@router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int,
                      db: AsyncSession = Depends(get_db)):
    """
    Удаление пользователя по ID.
    :param user_id: ID пользователя
    :param db: Сессия подключения к БД
    :return: Удалённый пользователь
    """
    user_service = UserService(db)
    return await user_service.delete_user(user_id)