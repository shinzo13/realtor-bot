from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext
from app.forms.realty_filter_form import SetupRealtyFilterForm
from app.keyboards.filter_keyboards import building_status_kb, room_count_kb, search_address_kb
from app.modules.realtor.utils import search_address

from uuid import uuid4
from app.config import env

router = Router()

@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите тип жилья:", reply_markup=building_status_kb())
    await state.set_state(SetupRealtyFilterForm.choosing_building_status)

@router.callback_query(SetupRealtyFilterForm.choosing_building_status)
async def building_status_chosen(callback: CallbackQuery, state: FSMContext):
    await state.update_data(building_status=callback.data.split("_")[1])
    await callback.message.edit_text("Сколько комнат вам нужно?", reply_markup=room_count_kb())
    await state.set_state(SetupRealtyFilterForm.choosing_rooms)
    await callback.answer()

@router.callback_query(SetupRealtyFilterForm.choosing_rooms)
async def rooms_chosen(callback: CallbackQuery, state: FSMContext):
    await state.update_data(room_count=callback.data.split("_")[1])
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
            input_message_content=InputTextMessageContent(message_text=address.text)
        )
        for address in addresses if address.kind not in env.bot.address_blacklist
    ]
    await query.answer(results, cache_time=1) # TODO choose cache time

@router.message(SetupRealtyFilterForm.entering_address)
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