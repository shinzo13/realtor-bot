from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext
from app.states.filter_states import FilterStates
from app.keyboards.filter_keyboards import building_status_kb, room_count_kb, search_address_kb
from app.modules.realtor.utils import search_address

from uuid import uuid4

router = Router()

@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите тип жилья:", reply_markup=building_status_kb())
    await state.set_state(FilterStates.choosing_building_status)

@router.callback_query(FilterStates.choosing_building_status)
async def building_status_chosen(callback: CallbackQuery, state: FSMContext):
    await state.update_data(building_status=callback.data.split("_")[1])
    await callback.message.edit_text("Сколько комнат вам нужно?", reply_markup=room_count_kb())
    await state.set_state(FilterStates.choosing_rooms)
    await callback.answer()

@router.callback_query(FilterStates.choosing_rooms)
async def rooms_chosen(callback: CallbackQuery, state: FSMContext):
    await state.update_data(room_count=callback.data.split("_")[1])
    await callback.message.edit_text("Выберите адрес, нажав на кнопку ниже:", reply_markup=search_address_kb())
    await state.set_state(FilterStates.entering_address)
    await callback.answer()

@router.inline_query(FilterStates.entering_address)
async def address_inline_query(query: InlineQuery, state: FSMContext):
    results = []
    addresses = await search_address(query.query)  # вернёт список словарей с адресами
    if not addresses:
        await query.answer(results=[])
        return
    for address in addresses:
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=f"📍{address.text}",
                description=address.tag,
                input_message_content=InputTextMessageContent(message_text=address.text)
            )
        )
    await query.answer(results, cache_time=1) # TODO choose cache time

@router.message(FilterStates.entering_address)
async def address_chosen(message: Message, state: FSMContext, bot_username: str):
    if not message.via_bot or message.via_bot.username != bot_username:
        await message.answer(
            "⚠️ Пожалуйста, выберите адрес через инлайн-режим, нажав на кнопку ниже.",
            reply_markup=search_address_kb()
        )
        return
    await state.update_data(address=message.text)
    data = await state.get_data()
    await message.answer(f"✅ Готово! Вы выбрали:\n"
                         f"- Тип жилья: {data['building_status']}\n"
                         f"- Комнат: {data['room_count']}\n"
                         f"- Адрес: {data['address']}")
    await state.clear()