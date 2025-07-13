import asyncio
import logging

from app.db.session import sessionmaker
from app.db.cruds import NotificationCRUD

from app.db.models import Offer

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, bot):
        self.bot = bot
        self.is_running = False

    async def start_sending(self, send_interval: int = 30):  # 30 секунд
        """Запустить отправку уведомлений"""
        self.is_running = True
        logger.info("Starting notification service...")

        while self.is_running:
            try:
                await self._send_pending_notifications()
                await asyncio.sleep(send_interval)
            except Exception as e:
                logger.error(f"Error in notification cycle: {e}")
                await asyncio.sleep(10)

    def stop_sending(self):
        """Остановить отправку уведомлений"""
        self.is_running = False
        logger.info("Stopping notification service...")

    async def _send_pending_notifications(self):
        """Отправить ожидающие уведомления"""
        async with sessionmaker() as session:
            notification_crud = NotificationCRUD(session)

            # Получаем неотправленные уведомления
            notifications = await notification_crud.get_pending_notifications(limit=50)

            for notification in notifications:
                try:
                    await self._send_notification(notification)
                    await notification_crud.mark_notification_sent(notification.id)
                except Exception as e:
                    logger.error(f"Error sending notification {notification.id}: {e}")

    async def _send_notification(self, notification):
        """Отправить одно уведомление"""
        offer = notification.offer

        # Формируем текст сообщения
        message_text = self._format_offer_message(offer)

        try:
            if offer.photo_url:
                await self.bot.send_photo(
                    chat_id=notification.user_id,
                    photo=offer.photo_url,
                    caption=message_text,
                    parse_mode='HTML'
                )
            else:
                await self.bot.send_message(
                    chat_id=notification.user_id,
                    text=message_text,
                    parse_mode='HTML',
                    disable_web_page_preview=False
                )
        except Exception as e:
            logger.error(f"Failed to send message to user {notification.user_id}: {e}")
            raise

    def _format_offer_message(self, offer: Offer) -> str:
        """Форматировать сообщение об объявлении"""
        message = f"🏠 <b>Новое объявление!</b>\n\n"
        # message += f"<b>{offer.title}</b>\n"
        message += f"<b>{offer.info}</b>\n"
        message += f"💰 <i>{offer.price} ({offer.deal_terms})</i>\n"

        message += f"📍 {offer.address}\n\n"

        # if offer.description and len(offer.description) > 0:
        #     # Обрезаем описание если слишком длинное
        #     desc = offer.description[:200] + "..." if len(offer.description) > 200 else offer.description
        #     message += f"\n📝 {desc}\n"
        message += f"<blockquote expandable>{offer.description}</blockquote>\n\n"

        message += f"\n🔗 <a href='{offer.url}'>Смотреть на ЦИАН</a>"

        return message