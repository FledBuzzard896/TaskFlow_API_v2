from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models.users import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all(self) -> list[User]:
        query = select(User)
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def create(self, data: dict) -> User:
        user = User(**data)
        self.session.add(user)
        try:
            await self.session.commit()
            await self.session.refresh(user)
        except Exception as e:
            await self.session.rollback()
            raise e
        return user


    async def update(self, user_id: int, update_data: dict) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        for key, value in update_data.items():
            setattr(user, key, value)
        try:
            await self.session.commit()
            await self.session.refresh(user)
        except Exception as e:
            await self.session.rollback()
            raise e
        return user


    async def delete(self, user: User) -> None:
        try:
            await self.session.delete(user)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e