from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models import Notification
from typing import List, Dict, Any
from datetime import datetime, UTC

class NotificationCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_notification(self, user_id: int, offer_id: int) -> Notification:
        """Создать уведомление"""
        notification = Notification(user_id=user_id, offer_id=offer_id)
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def bulk_create_notifications(self, notifications_data: List[Dict[str, Any]]) -> List[Notification]:
        """Массовое создание уведомлений"""
        notifications = [Notification(**data) for data in notifications_data]
        self.session.add_all(notifications)
        await self.session.commit()
        return notifications

    async def get_pending_notifications(self, limit: int = 100) -> List[Notification]:
        """Получить неотправленные уведомления"""
        stmt = (
            select(Notification)
            .where(Notification.is_sent == False)
            .order_by(Notification.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_notification_sent(self, notification_id: int):
        """Отметить уведомление как отправленное"""
        notification = await self.session.get(Notification, notification_id)
        if notification:
            notification.is_sent = True
            notification.sent_at = datetime.now(UTC)
            await self.session.commit()

    async def notification_exists(self, user_id: int, offer_id: int) -> bool:
        """Проверить существование уведомления"""
        stmt = select(Notification).where(
            and_(Notification.user_id == user_id, Notification.offer_id == offer_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None