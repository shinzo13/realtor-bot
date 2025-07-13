from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models import Offer, RealtyFilter
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC


class OfferCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_offer(self, offer_data: Dict[str, Any]) -> Offer:
        """Создать новое объявление"""
        offer = Offer(**offer_data)
        self.session.add(offer)
        await self.session.commit()
        await self.session.refresh(offer)
        return offer

    async def get_offer(self, offer_id: int) -> Optional[Offer]:
        """Получить объявление по ID"""
        stmt = select(Offer).where(Offer.offer_id == offer_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def offer_exists(self, offer_id: int) -> bool:
        """Проверить существование объявления"""
        stmt = select(Offer.offer_id).where(Offer.offer_id == offer_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def bulk_create_offers(self, offers: list[Offer]):
        """Массовое создание объявлений"""
        self.session.add_all(offers)
        return await self.session.commit()

    async def get_new_offers(self, limit: int = 1000) -> List[Offer]:
        """Получить необработанные объявления"""
        stmt = (
            select(Offer)
            .where(and_(Offer.is_processed == False, Offer.is_active == True))
            .order_by(Offer.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_offers_processed(self, offer_ids: List[int]):
        """Отметить объявления как обработанные"""
        stmt = (
            select(Offer)
            .where(Offer.offer_id.in_(offer_ids))
        )
        result = await self.session.execute(stmt)
        offers = result.scalars().all()

        for offer in offers:
            offer.is_processed = True

        await self.session.commit()

    async def filter_offers_by_criteria(self, realty_filter: RealtyFilter, offers: List[Offer]) -> List[Offer]:
        """Фильтровать объявления по критериям пользователя"""
        filtered_offers = []

        for offer in offers:
            # Проверяем количество комнат
            if realty_filter.rooms and offer.rooms not in realty_filter.rooms:
                continue

            # Проверяем цену
            if realty_filter.min_price and offer.price < realty_filter.min_price:
                continue
            if realty_filter.max_price and offer.price > realty_filter.max_price:
                continue

            # Проверяем залог
            if realty_filter.no_deposit and offer.has_deposit:
                continue

            # Проверяем животных
            if realty_filter.pets and not offer.pets_allowed:
                continue

            # Проверяем детей
            if realty_filter.kids and not offer.kids_allowed:
                continue

            # Проверяем ключевые слова в описании
            if realty_filter.keywords:
                text_to_search = f"{offer.title} {offer.description or ''}".lower()
                if not any(keyword.lower() in text_to_search for keyword in realty_filter.keywords):
                    continue

            # Проверяем адрес (простое вхождение)
            if realty_filter.address and realty_filter.address.lower() not in offer.address.lower():
                continue

            filtered_offers.append(offer)

        return filtered_offers

    async def deactivate_old_offers(self, days: int = 30):
        """Деактивировать старые объявления"""
        cutoff_date = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)

        stmt = (
            select(Offer)
            .where(and_(Offer.created_at < cutoff_date, Offer.is_active == True))
        )
        result = await self.session.execute(stmt)
        old_offers = result.scalars().all()

        for offer in old_offers:
            offer.is_active = False

        await self.session.commit()
        return len(old_offers)


