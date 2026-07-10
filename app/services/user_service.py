from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.repositories.user_repository import UserRepository



class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)


    async def get_or_create_user(self, current_user: dict) -> User:
        username = current_user.get("preferred_username")

        user = await self.user_repo.get_by_username(username)
        if user:
            return user

        # Если пользователь не найден, создаём нового
        email = current_user.get("email")
        full_name = current_user.get("name")

        new_user_data = {
            "username": username,
            "email": email or f"{username}@example.com",
            "full_name": full_name or username,
            "is_active": True,
        }
        return await self.user_repo.create(new_user_data)


    async def get_all_users(self, current_user: dict) -> list[User]:
        if "admin" not in current_user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только админ может просматривать всех пользователей"
            )
        return await self.user_repo.get_all()


    async def get_user_by_id(self, user_id: int, current_user: dict) -> User | None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь с таким ID не найден"
            )
        # Проверяем, что это либо сам пользователь, либо админ
        current_user_obj = await self.get_or_create_user(current_user)
        if current_user_obj.id != user_id and "admin" not in current_user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав"
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


    async def update_user(self, user_id: int, update_data: dict, current_user: dict) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        current_user_obj = await self.get_or_create_user(current_user)
        if current_user_obj.id != user_id and "admin" not in current_user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав"
            )

        # Проверка уникальности username (если передано)
        if "username" in update_data:
            existing = await self.user_repo.get_by_username(update_data["username"])
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username уже занят"
                )
        return await self.user_repo.update(user, update_data)


    async def delete_user(self, user_id: int, current_user: dict) -> User:
        if "admin" not in current_user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав"
            )
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        await self.user_repo.delete(user)
        return user