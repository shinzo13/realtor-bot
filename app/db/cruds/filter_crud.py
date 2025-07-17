from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models import RealtyFilter
from app.db.enums import RealtyType
from typing import Optional, List

class RealtyFilterCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_filter(self, user_id: int) -> Optional[RealtyFilter]:
        """Получить фильтр пользователя"""
        stmt = select(RealtyFilter).where(RealtyFilter.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_filter(self, user_id: int, **kwargs) -> RealtyFilter:
        """Создать фильтр для пользователя"""
        filter_data = {
            'user_id': user_id,
            'realty_type': kwargs.get('realty_type', RealtyType.FLAT),
            'apartment': kwargs.get('apartment', False),
            'rooms': kwargs.get('rooms', []),
            'address': kwargs.get('address', ''),
            'address_kind': kwargs.get('address_kind', ''),
            'min_price': kwargs.get('min_price'),
            'max_price': kwargs.get('max_price'),
            'no_deposit': kwargs.get('no_deposit', False),
            'kids': kwargs.get('kids', False),
            'pets': kwargs.get('pets', False),
            'renovation': kwargs.get('renovation', []),
            'keywords': kwargs.get('keywords', []),
            'initial_check_completed': kwargs.get('initial_check_completed', False)
        }

        realty_filter = RealtyFilter(**filter_data)
        self.session.add(realty_filter)
        await self.session.commit()
        await self.session.refresh(realty_filter)
        return realty_filter

    async def update_filter(self, user_id: int, **kwargs) -> Optional[RealtyFilter]:
        """Обновить фильтр пользователя"""
        realty_filter = await self.get_filter(user_id)
        if not realty_filter:
            return None

        for key, value in kwargs.items():
            if hasattr(realty_filter, key):
                setattr(realty_filter, key, value)

        await self.session.commit()
        await self.session.refresh(realty_filter)
        return realty_filter

    async def create_or_update_filter(self, user_id: int, **kwargs) -> RealtyFilter:
        """Создать или обновить фильтр"""
        existing_filter = await self.get_filter(user_id)
        if existing_filter:
            return await self.update_filter(user_id, **kwargs)
        else:
            return await self.create_filter(user_id, **kwargs)

    async def delete_filter(self, user_id: int) -> bool:
        """Удалить фильтр пользователя"""
        realty_filter = await self.get_filter(user_id)
        if realty_filter:
            await self.session.delete(realty_filter)
            await self.session.commit()
            return True
        return False

    async def get_all_filters(self) -> List[RealtyFilter]:
        """Получить все фильтры"""
        stmt = select(RealtyFilter).options(selectinload(RealtyFilter.user))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_filters_by_type(self, realty_type: RealtyType) -> List[RealtyFilter]:
        """Получить фильтры по типу недвижимости"""
        stmt = select(RealtyFilter).where(RealtyFilter.realty_type == realty_type)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_initial_check_completed(self, user_id: int) -> bool:
        """Отметить что первичная проверка объявлений завершена"""
        realty_filter = await self.get_filter(user_id)
        if realty_filter:
            realty_filter.initial_check_completed = True
            await self.session.commit()
            return True
        return False