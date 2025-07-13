import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka
from app.forms.realty_filter_form import SetupRealtyFilterForm
from app.keyboards.filter_keyboards import building_status_kb, room_count_kb, search_address_kb
from app.modules.realtor.utils import search_address
from app.db.cruds import UserCRUD, RealtyFilterCRUD
from app.db.enums import RealtyType
from uuid import uuid4
from app.config import env

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "/start")
async def start(
        message: Message,
        state: FSMContext,
        user_crud: FromDishka[UserCRUD]
):
    await state.clear()

    # Создаем или получаем пользователя
    user = await user_crud.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    logger.info(f"Created/got user: {user}")
    await message.answer("Выберите тип жилья:", reply_markup=building_status_kb())
    await state.set_state(SetupRealtyFilterForm.choosing_building_status)


@router.callback_query(SetupRealtyFilterForm.choosing_building_status)
async def building_status_chosen(callback: CallbackQuery, state: FSMContext):
    building_type = callback.data.split("_")[1]
    await state.update_data(building_status=building_type)
    await callback.message.edit_text("Сколько комнат вам нужно?", reply_markup=room_count_kb())
    await state.set_state(SetupRealtyFilterForm.choosing_rooms)
    await callback.answer()


@router.callback_query(SetupRealtyFilterForm.choosing_rooms)
async def rooms_chosen(callback: CallbackQuery, state: FSMContext):
    room_count = callback.data.split("_")[1]
    await state.update_data(room_count=room_count)
    await callback.message.edit_text("Выберите адрес, нажав на кнопку ниже:", reply_markup=search_address_kb())
    await state.set_state(SetupRealtyFilterForm.entering_address)
    await callback.answer()


@router.inline_query(SetupRealtyFilterForm.entering_address)
async def address_inline_query(query: InlineQuery):
    results = []
    addresses = await search_address(query.query)
    if not addresses:
        await query.answer(results=[])
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"📍{address.text}",
            description=address.kind,
            input_message_content=InputTextMessageContent(message_text=f"{address.text}|{address.kind}")
        )
        for address in addresses if address.kind not in env.bot.address_blacklist
    ]
    await query.answer(results, cache_time=1)


@router.message(SetupRealtyFilterForm.entering_address)
async def address_chosen(
        message: Message,
        state: FSMContext,
        bot_username: str,
        filter_crud: FromDishka[RealtyFilterCRUD]
):
    if not message.via_bot or message.via_bot.username != bot_username:
        await message.answer(
            "⚠️ Пожалуйста, выберите адрес через инлайн-режим, нажав на кнопку ниже.",
            reply_markup=search_address_kb()
        )
        return

    # Парсим адрес и тип
    address_data = message.text.split('|')
    address_text = address_data[0]
    address_kind = address_data[1] if len(address_data) > 1 else "unknown"

    await state.update_data(address=address_text, address_kind=address_kind)
    data = await state.get_data()

    # Сохраняем фильтр в базу данных
    realty_type = RealtyType.FLAT if data['building_status'] == 'new' else RealtyType.HOUSE
    rooms = int(data['room_count'])

    filterr = await filter_crud.create_or_update_filter(
        user_id=message.from_user.id,
        realty_type=realty_type,
        rooms=rooms,
        address=address_text,
        address_kind=address_kind,
        apartment=False,  # По умолчанию
        min_price=None,  # Можно добавить в форму
        max_price=None,  # Можно добавить в форму
        no_deposit=False,  # По умолчанию
        kids=False,  # По умолчанию
        pets=False,  # По умолчанию
        renovation=[],  # По умолчанию
        keywords=[]  # По умолчанию
    )
    logger.info(f"Created/updated filter: {filterr}")

    await message.answer(
        f"✅ Фильтр сохранен!\n"
        f"- Тип жилья: {data['building_status']}\n"
        f"- Комнат: {data['room_count']}\n"
        f"- Адрес: {address_text}\n"
        f"- Тип адреса: {address_kind}"
    )
    await state.clear()


@router.message(F.text == "/filter")
async def show_filter(
        message: Message,
        filter_crud: FromDishka[RealtyFilterCRUD]
):
    """Показать текущий фильтр пользователя"""
    realty_filter = await filter_crud.get_filter(message.from_user.id)

    if not realty_filter:
        await message.answer("У вас нет активного фильтра. Используйте /start для создания.")
        return

    filter_text = f"🔍 Ваш фильтр:\n"
    filter_text += f"- Тип: {realty_filter.realty_type.value}\n"
    filter_text += f"- Апартаменты: {'Да' if realty_filter.apartment else 'Нет'}\n"
    filter_text += f"- Комнат: {', '.join(map(str, realty_filter.rooms))}\n"
    filter_text += f"- Адрес: {realty_filter.address}\n"

    if realty_filter.min_price or realty_filter.max_price:
        price_range = f"{realty_filter.min_price or 0} - {realty_filter.max_price or '∞'}"
        filter_text += f"- Цена: {price_range}\n"

    if realty_filter.no_deposit:
        filter_text += "- Без залога: Да\n"
    if realty_filter.kids:
        filter_text += "- С детьми: Да\n"
    if realty_filter.pets:
        filter_text += "- С животными: Да\n"

    if realty_filter.renovation:
        filter_text += f"- Ремонт: {', '.join(realty_filter.renovation)}\n"

    if realty_filter.keywords:
        filter_text += f"- Ключевые слова: {', '.join(realty_filter.keywords)}\n"

    await message.answer(filter_text)


@router.message(F.text == "/delete_filter")
async def delete_filter(
        message: Message,
        filter_crud: FromDishka[RealtyFilterCRUD]
):
    """Удалить фильтр пользователя"""
    success = await filter_crud.delete_filter(message.from_user.id)

    if success:
        await message.answer("✅ Фильтр удален!")
    else:
        await message.answer("❌ Фильтр не найден.")