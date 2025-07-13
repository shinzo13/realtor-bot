from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from dishka.integrations.aiogram import FromDishka
from app.db.cruds import UserCRUD, RealtyFilterCRUD, OfferCRUD, NotificationCRUD
from app.config import env

router = Router()

# Список админов (добавьте свой user_id)
ADMIN_IDS = [123456789]  # Замените на реальные ID админов


def is_admin(message: Message) -> bool:
    return message.from_user.id in ADMIN_IDS


@router.message(Command("stats"))
async def get_stats(
        message: Message,
        user_crud: FromDishka[UserCRUD],
        filter_crud: FromDishka[RealtyFilterCRUD],
        offer_crud: FromDishka[OfferCRUD],
        notification_crud: FromDishka[NotificationCRUD]
):
    """Получить статистику бота (только для админов)"""
    if not is_admin(message):
        await message.answer("❌ Недостаточно прав")
        return

    try:
        # Получаем статистику
        users = await user_crud.get_active_users()
        filters = await filter_crud.get_all_filters()
        new_offers = await offer_crud.get_new_offers(limit=1000)
        pending_notifications = await notification_crud.get_pending_notifications(limit=1000)

        stats_text = f"📊 <b>Статистика бота</b>\n\n"
        stats_text += f"👥 Активных пользователей: {len(users)}\n"
        stats_text += f"🔍 Активных фильтров: {len(filters)}\n"
        stats_text += f"🏠 Новых объявлений: {len(new_offers)}\n"
        stats_text += f"📬 Ожидающих отправки: {len(pending_notifications)}\n"

        await message.answer(stats_text, parse_mode='HTML')

    except Exception as e:
        await message.answer(f"❌ Ошибка получения статистики: {e}")


@router.message(Command("cleanup"))
async def cleanup_old_data(
        message: Message,
        offer_crud: FromDishka[OfferCRUD]
):
    """Очистка старых данных (только для админов)"""
    if not is_admin(message):
        await message.answer("❌ Недостаточно прав")
        return

    try:
        # Деактивируем объявления старше 30 дней
        count = await offer_crud.deactivate_old_offers(days=30)

        await message.answer(f"✅ Деактивировано {count} старых объявлений")

    except Exception as e:
        await message.answer(f"❌ Ошибка очистки: {e}")


@router.message(Command("broadcast"))
async def broadcast_message(message: Message, user_crud: FromDishka[UserCRUD]):
    """Рассылка сообщения всем пользователям (только для админов)"""
    if not is_admin(message):
        await message.answer("❌ Недостаточно прав")
        return

    # Проверяем, есть ли текст для рассылки
    if not message.reply_to_message or not message.reply_to_message.text:
        await message.answer("❌ Ответьте на сообщение, которое хотите разослать")
        return

    try:
        broadcast_text = message.reply_to_message.text
        users = await user_crud.get_active_users()

        success_count = 0
        error_count = 0

        status_message = await message.answer(f"📤 Начинаю рассылку для {len(users)} пользователей...")

        for user in users:
            try:
                await message.bot.send_message(
                    chat_id=user.user_id,
                    text=broadcast_text
                )
                success_count += 1
            except Exception:
                error_count += 1

        await status_message.edit_text(
            f"✅ Рассылка завершена!\n"
            f"Успешно: {success_count}\n"
            f"Ошибок: {error_count}"
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка рассылки: {e}")


@router.message(Command("test_monitoring"))
async def test_monitoring(
        message: Message,
        filter_crud: FromDishka[RealtyFilterCRUD]
):
    """Тестирование мониторинга для конкретного пользователя"""
    if not is_admin(message):
        await message.answer("❌ Недостаточно прав")
        return

    try:
        # Проверяем фильтр админа
        realty_filter = await filter_crud.get_filter(message.from_user.id)

        if not realty_filter:
            await message.answer("❌ У вас нет активного фильтра для тестирования")
            return

        # Импортируем и тестируем мониторинг
        from app.modules.realtor.cian import CianClient

        cian_client = CianClient()
        offers = await cian_client.get_offers(realty_filter)

        await message.answer(
            f"🔍 Найдено {len(offers)} объявлений по вашему фильтру\n"
            f"Тип: {realty_filter.realty_type.value}\n"
            f"Комнат: {realty_filter.rooms}\n"
            f"Адрес: {realty_filter.address}"
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка тестирования: {e}")