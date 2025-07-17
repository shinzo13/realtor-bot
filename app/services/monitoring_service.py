import asyncio
import logging
from app.db.session import sessionmaker
from app.db.cruds import RealtyFilterCRUD, OfferCRUD, NotificationCRUD
from app.modules.realtor.cian import CianClient
from app.db.models import RealtyFilter

logger = logging.getLogger(__name__)


class MonitoringService:
    def __init__(self):
        self.cian_client = CianClient()
        self.is_running = False

    async def start_monitoring(self, check_interval: int = 300):  # 5 минут
        """Запустить мониторинг объявлений"""
        self.is_running = True
        logger.info("Starting monitoring service...")

        while self.is_running:
            try:
                await self._check_new_offers()
                await asyncio.sleep(check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(60)  # Подождать минуту при ошибке

    def stop_monitoring(self):
        """Остановить мониторинг"""
        self.is_running = False
        logger.info("Stopping monitoring service...")

    async def _check_new_offers(self):
        """Проверить новые объявления для всех пользователей"""
        async with sessionmaker() as session:
            filter_crud = RealtyFilterCRUD(session)
            offer_crud = OfferCRUD(session)
            notification_crud = NotificationCRUD(session)

            # Получаем все активные фильтры
            filters = await filter_crud.get_all_filters()
            logger.info(f"Checking {len(filters)} active filters")

            for realty_filter in filters:
                try:
                    await self._process_filter(realty_filter, offer_crud, notification_crud)
                except Exception as e:
                    logger.error(f"Error processing filter for user {realty_filter.user_id}: {e}")

    async def _process_filter(
        self,
        realty_filter: RealtyFilter,
        offer_crud: OfferCRUD,
        notification_crud: NotificationCRUD
    ):
        """Обработать фильтр пользователя"""
        try:
            # Получаем объявления с ЦИАН
            cian_offers = await self.cian_client.get_offers(realty_filter)
            logger.info(f"Found {len(cian_offers)} offers for user {realty_filter.user_id}")

            # Сохраняем все объявления если их еще нет в базе
            offers_to_save = []
            for offer in cian_offers:
                if not await offer_crud.offer_exists(offer.offer_id):
                    offers_to_save.append(offer)

            if offers_to_save:
                await offer_crud.bulk_create_offers(offers_to_save)
                logger.info(f"Saved {len(offers_to_save)} new offers to database")

            # Создаем уведомления только если первичная проверка завершена
            if realty_filter.initial_check_completed:
                notifications_data = []
                for offer in cian_offers:
                    # Проверяем был ли оффер уже показан этому пользователю
                    if not await notification_crud.notification_exists(realty_filter.user_id, offer.offer_id):
                        notifications_data.append({
                            'user_id': realty_filter.user_id,
                            'offer_id': offer.offer_id
                        })

                if notifications_data:
                    await notification_crud.bulk_create_notifications(notifications_data)
                    logger.info(f"Created {len(notifications_data)} notifications for user {realty_filter.user_id}")
                else:
                    logger.info(f"No new notifications for user {realty_filter.user_id} - all offers already shown")
            else:
                logger.info(f"Skipping notifications for user {realty_filter.user_id} - initial check not completed yet")

        except Exception as e:
            logger.error(f"Error in _process_filter for user {realty_filter.user_id}: {e}")


