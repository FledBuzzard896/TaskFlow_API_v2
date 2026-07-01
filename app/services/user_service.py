from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.repositories.user_repository import UserRepository



class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)


    async def get_by_id(self, user_id: int) -> User | None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь с таким ID не найден"
            )
        return user


    async def create_user(self, data: dict) -> User:
        # Проверка уникальности username
        if await self.user_repo.get_by_username(data.get("username")):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Этот username уже занят"
            )
        return await self.user_repo.create(data)


    async def update_user(self, user_id: int, update_data: dict) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        # Проверка уникальности username (если передано)
        if "username" in update_data:
            existing = await self.user_repo.get_by_username(update_data["username"])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username уже занят")
        # Обновляем поля
        for key, value in update_data.items():
            setattr(user, key, value)
        return await self.user_repo.update(user)


    async def delete_user(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        await self.user_repo.delete(user)
        return user