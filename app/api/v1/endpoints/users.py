from typing import List
from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.users import UserResponse, UserCreate, UserUpdate
from app.services.user_service import UserService


public_router = APIRouter(
    tags=["users"],
)
protected_router = APIRouter(
    tags=["users"],
)


@protected_router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_service = UserService(db)
    user = await user_service.get_or_create_user(current_user)
    return user


@protected_router.get("/users", response_model=List[UserResponse])
async def print_users(
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """ Получить список всех пользователей. """
    user_service = UserService(db)
    return await user_service.get_all_users(current_user)


# Регистрация - открытый эндпоинт (без токена)
@public_router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        data: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Создание нового пользователя.
    Проверка на уникальность username.
    """
    user_service = UserService(db)
    return await user_service.create_user(data.model_dump())


@protected_router.get("/users/{user_id}", response_model=UserResponse)
async def print_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """ Получить пользователя по ID. """
    user_service = UserService(db)
    return await user_service.get_user_by_id(user_id, current_user)


@protected_router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int,
        update_data: UserUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """
    Частичное обновление пользователя.
    При смене username проверяет, что имя не занято другим пользователем.
    """
    user_service = UserService(db)
    return await user_service.update_user(user_id,  update_data.model_dump(exclude_unset=True), current_user)


@protected_router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """ Удаление пользователя по ID. """
    user_service = UserService(db)
    return await user_service.delete_user(user_id, current_user)