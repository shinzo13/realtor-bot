from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers import user_filters
from app.di.container import setup_di
from app.db.session import init_db
from app.services import MonitoringService, NotificationService
import logging
import asyncio
import sys
import signal
from app.config import env

logger = logging.getLogger(__name__)


class BotApplication:
    def __init__(self):
        self.bot = None
        self.dp = None
        self.monitoring_service = None
        self.notification_service = None
        self.tasks = []
        self.is_running = True

    async def start(self):
        """Запуск всего приложения"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)]
        )

        # Инициализация базы данных
        await init_db()
        logger.info("Database initialized")

        # Создание бота и диспетчера
        self.bot = Bot(token=env.bot.token.get_secret_value())
        self.dp = Dispatcher(storage=MemoryStorage())

        # Настройка DI
        setup_di(self.dp)

        # Подключение роутеров
        from app.handlers import admin
        self.dp.include_router(user_filters.router)
        self.dp.include_router(admin.router)

        self.bot_username = (await self.bot.me()).username

        # Создание сервисов
        self.monitoring_service = MonitoringService()
        self.notification_service = NotificationService(self.bot)

        # Настройка обработки сигналов для graceful shutdown
        self._setup_signal_handlers()

        # Запуск всех компонентов
        await self._start_all_services()

    def _setup_signal_handlers(self):
        """Настройка обработчиков сигналов для корректного завершения"""

        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.is_running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def _start_all_services(self):
        """Запуск всех сервисов параллельно"""
        try:
            # Создаем задачи для всех сервисов
            polling_task = asyncio.create_task(
                self._start_polling(),
                name="bot_polling"
            )

            monitoring_task = asyncio.create_task(
                self.monitoring_service.start_monitoring(check_interval=20),  # 5 минут
                name="monitoring"
            )

            notification_task = asyncio.create_task(
                self.notification_service.start_sending(send_interval=10),  # 30 секунд
                name="notifications"
            )

            self.tasks = [polling_task, monitoring_task, notification_task]
            logger.info("All services started")

            # Ждем завершения любой из задач или сигнала остановки
            done, pending = await asyncio.wait(
                self.tasks,
                return_when=asyncio.FIRST_COMPLETED
            )

            # Если одна из задач завершилась, останавливаем остальные
            await self._shutdown()

        except Exception as e:
            logger.error(f"Error starting services: {e}")
            await self._shutdown()

    async def _start_polling(self):
        """Запуск поллинга бота"""
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot, bot_username=self.bot_username)

    async def _shutdown(self):
        """Корректное завершение работы всех сервисов"""
        logger.info("Shutting down services...")

        # Останавливаем сервисы
        if self.monitoring_service:
            self.monitoring_service.stop_monitoring()

        if self.notification_service:
            self.notification_service.stop_sending()

        # Отменяем все задачи
        for task in self.tasks:
            if not task.done():
                task.cancel()

        # Ждем завершения всех задач
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        # Закрываем сессию бота
        if self.bot:
            await self.bot.session.close()

        logger.info("Shutdown complete")


async def main():
    app = BotApplication()
    try:
        await app.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        logger.info("Application finished")


if __name__ == "__main__":
    asyncio.run(main())