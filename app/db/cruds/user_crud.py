from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models import User
from typing import Optional, List
from datetime import datetime, UTC


class UserCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        stmt = select(User).where(User.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_with_filter(self, user_id: int) -> Optional[User]:
        """Получить пользователя с фильтром"""
        stmt = select(User).options(selectinload(User.realty_filter)).where(User.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user_id: int, username: str = None, first_name: str = None,
                          last_name: str = None) -> User:
        """Создать пользователя"""
        user = User(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user_activity(self, user_id: int) -> None:
        """Обновить время последней активности"""
        user = await self.get_user(user_id)
        if user:
            user.last_activity = datetime.now(UTC)
            await self.session.commit()

    async def get_or_create_user(self, user_id: int, username: str = None, first_name: str = None,
                                 last_name: str = None) -> User:
        """Получить или создать пользователя"""
        user = await self.get_user(user_id)
        if not user:
            user = await self.create_user(user_id, username, first_name, last_name)
        else:
            await self.update_user_activity(user_id)
        return user

    async def deactivate_user(self, user_id: int) -> None:
        """Деактивировать пользователя"""
        user = await self.get_user(user_id)
        if user:
            user.is_active = False
            await self.session.commit()

    async def get_active_users(self) -> List[User]:
        """Получить всех активных пользователей"""
        stmt = select(User).where(User.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


