from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers import user_filters
import logging
import asyncio
import os, sys
from app.config import env
logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)] # костыль для логов в пичарме уберупотом
    )
    bot = Bot(token=env.bot.token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(user_filters.router)
    bot_username = (await bot.me()).username
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, bot_username=bot_username)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Exit")