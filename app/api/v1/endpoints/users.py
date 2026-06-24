from typing import List
from fastapi import HTTPException, status, APIRouter

from app.schemas.user import UserResponse, UserCreate, UserUpdate


router = APIRouter(
    tags=["users"],
)

users_db = []

@router.get("/users", response_model=List[UserResponse])
async def print_users():
    """
    Получить список всех пользователей.
    :return: Список пользователей
    """
    return users_db


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate):
    """
    Создать нового пользователя.
    Проверка на уникальность username.
    :param data: Данные для создания пользователя
    :return: Созданный пользователь
    """
    for user in users_db:
        if user.get("username") == data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Данный username уже занят",
            )

    new_user = data.dict()
    users_db.append(new_user)
    return new_user


@router.get("/users/{user_id}", response_model=UserResponse)
async def print_user(user_id: int):
    """
    Получить пользователя по ID.
    :param user_id: ID пользователя
    :return: Найденный пользователь
    """
    user = None
    for u in users_db:
        if u.get("id") == user_id:
            user = u
            break

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким ID не найден"
        )
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, update_data: UserUpdate):
    """
    Частичное обновление пользователя.
    При смене username проверяет, что имя не занято другим пользователем.
    :param user_id: ID пользователя
    :param update_data: Обновляемые поля
    :return: Обновлённый пользователь
    """
    user = None
    for u in users_db:
        if u.get("id") == user_id:
            user = u
            break

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким ID не найден"
        )

    update_dict = update_data.dict(exclude_unset=True)

    if "username" in update_dict:
        new_username = update_dict["username"]
        for u in users_db:
            if u["id"] != user_id and u["username"] == new_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Данный username уже занят другим пользователем"
                )

    for key, value in update_dict.items():
        if value is not None:
            user[key] = value
    return user


@router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int):
    """
    Удаление пользователя по ID.
    :param user_id: ID пользователя
    :return: Удалённый пользователь
    """
    user = None
    for u in users_db:
        if u.get("id") == user_id:
            user = u
            break

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким ID не найден"
        )

    users_db.remove(user)
    return user