import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka
from app.forms.realty_filter_form import SetupRealtyFilterForm
from app.keyboards.filter_keyboards import (
    realty_type_kb, apartment_value_kb, room_count_kb, search_address_kb,
    price_range_kb, other_filters_kb, renovation_kb, confirm_filter_kb,
    back_kb
)
from app.modules.realtor.utils import search_address
from app.db.cruds import UserCRUD, RealtyFilterCRUD
from app.db.enums import RealtyType, Renovation
from uuid import uuid4
from app.config import env
from app.modules.realtor.cian.client import CianClient

router = Router()
logger = logging.getLogger(__name__)


# ========== КОМАНДА СТАРТ ==========
@router.message(F.text == "/start")
async def start_command(
        message: Message,
        state: FSMContext,
        user_crud: FromDishka[UserCRUD]
):
    """Начать создание фильтра"""
    await state.clear()

    # Создаем или получаем пользователя
    user = await user_crud.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    logger.info(f"User {user.user_id} started filter setup")

    msg = await message.answer(
        "🏠 <b>Настройка фильтра поиска жилья</b>\n\n"
        "Давайте настроим ваш персональный фильтр для поиска жилья.\n\n"
        "Выберите тип жилья:",
        reply_markup=realty_type_kb(),
        parse_mode='HTML'
    )
    await state.update_data(msg_id=msg.message_id)
    await state.set_state(SetupRealtyFilterForm.choosing_realty_type)


# ========== ГЛОБАЛЬНАЯ ОБРАБОТКА КНОПКИ "НАЗАД" ==========
@router.callback_query(F.data == "back")
async def handle_back(callback: CallbackQuery, state: FSMContext):
    """Универсальная обработка кнопки 'Назад'"""
    current_state = await state.get_state()
    data = await state.get_data()

    if current_state == SetupRealtyFilterForm.choosing_apartment_value.state:
        # Возврат к выбору типа жилья
        await callback.message.edit_text(
            "🏠 <b>Настройка фильтра поиска жилья</b>\n\nВыберите тип жилья:",
            reply_markup=realty_type_kb(),
            parse_mode='HTML'
        )
        await state.set_state(SetupRealtyFilterForm.choosing_realty_type)

    elif current_state == SetupRealtyFilterForm.choosing_rooms.state:
        # Возврат к выбору типа квартир или типа жилья
        if data.get('building_type') == 'flat':
            await callback.message.edit_text(
                "🏢 <b>Тип квартир</b>\n\nВыберите тип квартир:",
                reply_markup=apartment_value_kb(),
                parse_mode='HTML'
            )
            await state.set_state(SetupRealtyFilterForm.choosing_apartment_value)
        else:
            await callback.message.edit_text(
                "🏠 <b>Настройка фильтра поиска жилья</b>\n\nВыберите тип жилья:",
                reply_markup=realty_type_kb(),
                parse_mode='HTML'
            )
            await state.set_state(SetupRealtyFilterForm.choosing_realty_type)

    elif current_state == SetupRealtyFilterForm.entering_address.state:
        if data.get('building_type') == 'flat':
            # Возврат к выбору комнат
            data = await state.get_data()
            selected_rooms = set(data.get('selected_rooms', []))
            await callback.message.edit_text(
                "🔢 <b>Количество комнат</b>\n\nВыберите нужное количество комнат:",
                reply_markup=room_count_kb(selected_rooms),
                parse_mode='HTML'
            )
            await state.set_state(SetupRealtyFilterForm.choosing_rooms)
        else:
            await callback.message.edit_text(
                "🏠 <b>Настройка фильтра поиска жилья</b>\n\nВыберите тип жилья:",
                reply_markup=realty_type_kb(),
                parse_mode='HTML'
            )
            await state.set_state(SetupRealtyFilterForm.choosing_realty_type)

    elif current_state == SetupRealtyFilterForm.entering_price_range.state:
        # Возврат к выбору адреса
        await callback.message.edit_text(
            "📍 <b>Местоположение</b>\n\nВыберите адрес для поиска жилья:",
            reply_markup=search_address_kb(),
            parse_mode='HTML'
        )
        await state.set_state(SetupRealtyFilterForm.entering_address)

    elif current_state == SetupRealtyFilterForm.entering_custom_min_price.state:
        # Возврат к выбору цены
        await callback.message.edit_text(
            "💰 <b>Ценовой диапазон</b>\n\nВыберите желаемый диапазон арендной платы:",
            reply_markup=price_range_kb(),
            parse_mode='HTML'
        )
        await state.set_state(SetupRealtyFilterForm.entering_price_range)

    elif current_state == SetupRealtyFilterForm.entering_custom_max_price.state:
        await callback.message.edit_text(
            "💰 <b>Свой диапазон</b>\n\nВведите минимальную стоимость (₽/мес.):",
            reply_markup=back_kb(),
            parse_mode='HTML'
        )
        await state.set_state(SetupRealtyFilterForm.entering_custom_min_price)

    elif current_state == SetupRealtyFilterForm.choosing_other.state:
        # Возврат к выбору цены
        await callback.message.edit_text(
            "💰 <b>Ценовой диапазон</b>\n\nВыберите желаемый диапазон арендной платы:",
            reply_markup=price_range_kb(),
            parse_mode='HTML'
        )
        await state.set_state(SetupRealtyFilterForm.entering_price_range)

    elif current_state == SetupRealtyFilterForm.choosing_renovation.state:
        # Возврат к дополнительным фильтрам
        data = await state.get_data()
        selected_other = set(data.get('selected_other_filters', []))
        await callback.message.edit_text(
            "✨ <b>Дополнительные условия</b>\n\nВыберите важные для вас условия:",
            reply_markup=other_filters_kb(selected_other),
            parse_mode='HTML'
        )
        await state.set_state(SetupRealtyFilterForm.choosing_other)

    elif current_state == SetupRealtyFilterForm.confirming_filter.state:
        # Возврат к выбору ремонта
        data = await state.get_data()
        selected_renovation = set(data.get('selected_renovations', []))
        await callback.message.edit_text(
            "🔨 <b>Тип ремонта</b>\n\nВыберите желаемые типы ремонта:",
            reply_markup=renovation_kb(selected_renovation),
            parse_mode='HTML'
        )
        await state.set_state(SetupRealtyFilterForm.choosing_renovation)

    await callback.answer()


# ========== ШАГ 1: ТИП ЖИЛЬЯ ==========
@router.callback_query(SetupRealtyFilterForm.choosing_realty_type)
async def handle_realty_type(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа жилья"""
    realty_type = callback.data.split("_")[1]  # flat или house
    await state.update_data(building_type=realty_type)

    if realty_type == "flat":
        # Для квартир переходим к выбору типа квартир
        await callback.message.edit_text(
            "🏢 <b>Тип квартир</b>\n\nВыберите тип квартир:",
            reply_markup=apartment_value_kb(),
            parse_mode='HTML'
        )
        await state.set_state(SetupRealtyFilterForm.choosing_apartment_value)
    else:
        # Для домов сразу к адресу
        await callback.message.edit_text(
            "📍 <b>Местоположение</b>\n\nВыберите адрес для поиска жилья:",
            reply_markup=search_address_kb(),
            parse_mode='HTML'
        )
        await state.set_state(SetupRealtyFilterForm.entering_address)

    await callback.answer()


# ========== ШАГ 2: ТИП КВАРТИР ==========
@router.callback_query(SetupRealtyFilterForm.choosing_apartment_value)
async def handle_apartment_type(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа квартир"""
    apartment_type = callback.data.split("_")[1]  # yes или no
    apartment = apartment_type == "yes"
    await state.update_data(apartment=apartment)

    await callback.message.edit_text(
        "🔢 <b>Количество комнат</b>\n\nВыберите нужное количество комнат:",
        reply_markup=room_count_kb(),
        parse_mode='HTML'
    )
    await state.set_state(SetupRealtyFilterForm.choosing_rooms)
    await callback.answer()


# ========== ШАГ 3: КОЛИЧЕСТВО КОМНАТ ==========
@router.callback_query(SetupRealtyFilterForm.choosing_rooms)
async def handle_rooms(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора количества комнат"""
    data = await state.get_data()
    selected_rooms = set(data.get('selected_rooms', []))

    if callback.data.startswith("room_"):
        # Переключение выбора комнаты
        room_num = int(callback.data.split("_")[1])
        if room_num in selected_rooms:
            selected_rooms.remove(room_num)
        else:
            selected_rooms.add(room_num)

        await state.update_data(selected_rooms=list(selected_rooms))
        await callback.message.edit_reply_markup(reply_markup=room_count_kb(selected_rooms))
        await callback.answer()

    elif callback.data == "rooms_confirm":
        # Подтверждение выбора
        if not selected_rooms:
            await callback.answer("❌ Выберите хотя бы один вариант комнат", show_alert=True)
            return

        await state.update_data(rooms=list(selected_rooms))
        await callback.message.edit_text(
            "📍 <b>Местоположение</b>\n\nВыберите адрес для поиска жилья:",
            reply_markup=search_address_kb(),
            parse_mode='HTML'
        )
        await state.set_state(SetupRealtyFilterForm.entering_address)
        await callback.answer()


# ========== ШАГ 4: АДРЕС ==========
@router.inline_query(SetupRealtyFilterForm.entering_address)
async def address_inline_search(query: InlineQuery):
    """Инлайн-поиск адресов"""
    results = []
    if query.query.strip():
        try:
            addresses = await search_address(query.query)
            results = [
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=f"📍 {address.text}",
                    description=address.kind,
                    input_message_content=InputTextMessageContent(
                        message_text=f"{address.kind}: {address.text}"
                    )
                )
                for address in addresses[:15]
                if address.kind not in env.bot.address_blacklist
            ]
        except Exception as e:
            logger.error(f"Error in address search: {e}")

    await query.answer(results, cache_time=1)


@router.message(SetupRealtyFilterForm.entering_address)
async def handle_address(message: Message, state: FSMContext, bot: Bot):
    """Обработка выбранного адреса"""
    bot_username = (await bot.get_me()).username
    if not message.via_bot or message.via_bot.username != bot_username:
        await message.answer(
            "<i>⚠️ Пожалуйста, выберите адрес через инлайн-поиск, нажав на кнопку выше.</i>",
            reply_markup=search_address_kb()
        )
        return
    # Парсим данные адреса
    address_data = message.text.split(': ', 1)
    address_text = address_data[1].strip()
    address_kind = address_data[0].strip()

    await state.update_data(address=address_text, address_kind=address_kind)
    await message.delete()
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=(await state.get_data())["msg_id"],
        text="💰 <b>Ценовой диапазон</b>\n\nВыберите желаемый диапазон арендной платы (₽/мес.):",
        reply_markup=price_range_kb(),
        parse_mode='HTML'
    )
    await state.set_state(SetupRealtyFilterForm.entering_price_range)


# ========== ШАГ 5: ЦЕНА ==========
@router.callback_query(SetupRealtyFilterForm.entering_price_range)
async def handle_price_range(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора ценового диапазона"""
    if callback.data == "price_any":
        await state.update_data(min_price=1, max_price=9999999)
    elif callback.data == "price_custom":
        await callback.message.edit_text(
            "💰 <b>Свой диапазон</b>\n\nВведите минимальную стоимость (₽/мес.):",
            reply_markup=back_kb(),
            parse_mode='HTML'
        )
        await state.set_state(SetupRealtyFilterForm.entering_custom_min_price)
        await callback.answer()
        return
    else:
        # Парсим готовый диапазон
        parts = callback.data.split("_")
        min_price = int(parts[1]) if parts[1] != "0" else 0
        max_price = int(parts[2]) if parts[2] != "0" else 9999999 # TODO kostl
        await state.update_data(min_price=min_price, max_price=max_price)

    await callback.message.edit_text(
        "✨ <b>Дополнительные условия</b>\n\nВыберите важные для вас условия:",
        reply_markup=other_filters_kb(),
        parse_mode='HTML'
    )
    await state.set_state(SetupRealtyFilterForm.choosing_other)
    await callback.answer()

@router.message(SetupRealtyFilterForm.entering_custom_min_price)
async def handle_custom_min_price(message: Message, state: FSMContext, bot: Bot):
    min_price = message.text.strip()
    await message.delete()
    if not min_price.isdigit():
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=(await state.get_data())["msg_id"],
            text="<i>⚠️ Пожалуйста, введите цену как число (43000, 8022 и т.д.):</i>",
            reply_markup=back_kb(),
            parse_mode='HTML'
        )
        return
    await state.update_data(min_price=int(min_price))
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=(await state.get_data())["msg_id"],
        text="💰 <b>Свой диапазон</b>\n\nВведите максимальную стоимость (₽/мес.):",
        reply_markup=back_kb(),
        parse_mode='HTML'
    )
    await state.set_state(SetupRealtyFilterForm.entering_custom_max_price)

@router.message(SetupRealtyFilterForm.entering_custom_max_price)
async def handle_custom_max_price(message: Message, state: FSMContext, bot: Bot):
    max_price = message.text.strip()
    await message.delete()
    if not max_price.isdigit():
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=(await state.get_data())["msg_id"],
            text="<i>⚠️ Пожалуйста, введите цену как число (43000, 8022 и т.д.):</i>",
            reply_markup=back_kb(),
            parse_mode='HTML'
        )
        return
    await state.update_data(max_price=int(max_price))
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=(await state.get_data())["msg_id"],
        text="✨ <b>Дополнительные условия</b>\n\nВыберите важные для вас условия:",
        reply_markup=other_filters_kb(),
        parse_mode='HTML'
    )
    await state.set_state(SetupRealtyFilterForm.choosing_other)

# ========== ШАГ 6: ДОПОЛНИТЕЛЬНЫЕ УСЛОВИЯ ==========
@router.callback_query(SetupRealtyFilterForm.choosing_other)
async def handle_other_filters(callback: CallbackQuery, state: FSMContext):
    """Обработка дополнительных условий (дети, животные, залог)"""
    state_data = await state.get_data()
    selected_other = set(state_data.get('selected_other_filters', []))

    if callback.data.startswith("other_") and callback.data != "other_confirm":
        # Переключение выбора условия
        filter_type = callback.data.split("_", 1)[1]
        if filter_type in selected_other:
            selected_other.remove(filter_type)
        else:
            selected_other.add(filter_type)

        await state.update_data(selected_other_filters=list(selected_other))
        await callback.message.edit_reply_markup(reply_markup=other_filters_kb(selected_other))
        await callback.answer()

    elif callback.data == "other_confirm":
        # Подтверждение и переход к ремонту
        # Устанавливаем значения на основе выбора
        kids = "kids" in selected_other
        pets = "pets" in selected_other
        no_deposit = "no_deposit" in selected_other

        await state.update_data(kids=kids, pets=pets, no_deposit=no_deposit)

        await callback.message.edit_text(
            "🔨 <b>Тип ремонта</b>\n\nВыберите желаемые типы ремонта:",
            reply_markup=renovation_kb(),
            parse_mode='HTML'
        )
        await state.set_state(SetupRealtyFilterForm.choosing_renovation)
        await callback.answer()


# ========== ШАГ 7: РЕМОНТ ==========
@router.callback_query(SetupRealtyFilterForm.choosing_renovation)
async def handle_renovation(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типов ремонта"""
    state_data = await state.get_data()
    selected_renovations = set(state_data.get('selected_renovations', []))

    if callback.data.startswith("renovation_") and callback.data != "renovation_confirm":
        # Переключение выбора ремонта
        renovation_type = callback.data.split("_")[1]

        if renovation_type == "any":
            # Если выбрали "Неважно", очищаем остальные
            selected_renovations = {"any"}
        else:
            # Убираем "Неважно" если выбираем конкретный тип
            selected_renovations.discard("any")

            if renovation_type in selected_renovations:
                selected_renovations.remove(renovation_type)
            else:
                selected_renovations.add(renovation_type)

        await state.update_data(selected_renovations=list(selected_renovations))
        await callback.message.edit_reply_markup(reply_markup=renovation_kb(selected_renovations))
        await callback.answer()

    elif callback.data == "renovation_confirm":
        # Подтверждение выбора ремонта
        if not selected_renovations:
            await callback.answer("❌ Выберите хотя бы один вариант", show_alert=True)
            return

        # Преобразуем в enum для сохранения (кроме "any")
        renovation_enums = []
        if "any" not in selected_renovations:
            renovation_mapping = {
                "cosmetic": Renovation.COSMETIC,
                "euro": Renovation.EURO,
                "designed": Renovation.DESIGNED
            }
            renovation_enums = [renovation_mapping[r] for r in selected_renovations if r in renovation_mapping]

        await state.update_data(renovation=renovation_enums)

        # Переход к подтверждению
        await show_filter_confirmation(callback.message, state)
        await callback.answer()


# ========== ПОДТВЕРЖДЕНИЕ ФИЛЬТРА ==========
async def show_filter_confirmation(message_obj, state: FSMContext):
    """Показать сводку фильтра для подтверждения"""
    data = await state.get_data()

    # Формируем текст сводки
    text = "📋 <b>Сводка вашего фильтра</b>\n\n"

    # Тип жилья
    building_type = "🏢 Квартира" if data['building_type'] == 'flat' else "🏠 Дом"
    text += f"🏠 <b>Тип жилья:</b> {building_type}\n"

    # Тип квартир (только для квартир)
    if data['building_type'] == 'flat':
        apt_text = "Апартаменты" if data.get('apartment') else "Обычные квартиры"
        text += f"🏢 <b>Тип квартир:</b> {apt_text}\n"

    # Комнаты
    rooms = data.get('rooms', [])
    room_names = []
    for room in sorted(rooms):
        if room == 9:
            room_names.append("Студия")
        else:
            room_names.append(f"{room} комн.")
    text += f"🔢 <b>Комнаты:</b> {', '.join(room_names)}\n"

    # Адрес
    text += f"📍 <b>Адрес:</b> {data.get('address', 'Не указан')}\n"

    # Цена
    min_price = data.get('min_price')
    max_price = data.get('max_price')
    if min_price or max_price:
        price_parts = []
        if min_price:
            price_parts.append(f"от {min_price:,}".replace(',', ' '))
        if max_price:
            price_parts.append(f"до {max_price:,}".replace(',', ' '))
        text += f"💰 <b>Цена:</b> {' '.join(price_parts)} ₽\n"
    else:
        text += f"💰 <b>Цена:</b> Любая\n"

    # Дополнительные условия
    conditions = []
    if data.get('kids'):
        conditions.append("С детьми")
    if data.get('pets'):
        conditions.append("С животными")
    if data.get('no_deposit'):
        conditions.append("Без залога")

    if conditions:
        text += f"✨ <b>Условия:</b> {', '.join(conditions)}\n"
    else:
        text += f"✨ <b>Условия:</b> Без ограничений\n"

    # Ремонт
    renovation = data.get('renovation', [])
    selected_reno = data.get('selected_renovations', [])

    if "any" in selected_reno:
        text += f"🔨 <b>Ремонт:</b> Любой\n"
    elif renovation:
        renovation_names = {
            Renovation.COSMETIC: "Косметический",
            Renovation.EURO: "Евроремонт",
            Renovation.DESIGNED: "Дизайнерский"
        }
        reno_text = ", ".join([renovation_names.get(r, str(r)) for r in renovation])
        text += f"🔨 <b>Ремонт:</b> {reno_text}\n"
    else:
        text += f"🔨 <b>Ремонт:</b> Любой\n"

    # Отправляем сообщение
    if hasattr(message_obj, 'edit_text'):
        await message_obj.edit_text(text, reply_markup=confirm_filter_kb(), parse_mode='HTML')
    else:
        await message_obj.answer(text, reply_markup=confirm_filter_kb(), parse_mode='HTML')

    await state.set_state(SetupRealtyFilterForm.confirming_filter)


@router.callback_query(SetupRealtyFilterForm.confirming_filter)
async def handle_filter_confirmation(callback: CallbackQuery, state: FSMContext,
                                     filter_crud: FromDishka[RealtyFilterCRUD]):
    """Обработка подтверждения фильтра"""
    if callback.data == "filter_save":
        # Сохраняем фильтр
        data = await state.get_data()

        try:
            # Определяем тип недвижимости
            realty_type = RealtyType.FLAT if data['building_type'] == 'flat' else RealtyType.HOUSE

            # Сохраняем в БД
            filter_obj = await filter_crud.create_or_update_filter(
                user_id=callback.from_user.id,
                realty_type=realty_type,
                apartment=data.get('apartment', False),
                rooms=data.get('rooms', []),
                address=data.get('address', ''),
                address_kind=data.get('address_kind', ''),
                min_price=data.get('min_price'),
                max_price=data.get('max_price'),
                no_deposit=data.get('no_deposit', False),
                kids=data.get('kids', False),
                pets=data.get('pets', False),
                renovation=data.get('renovation', []),
                keywords=data.get('keywords', [])
            )

            # Показываем информацию о поиске
            await callback.message.edit_text(
                "🔍 <b>Проверяем количество доступных объявлений...</b>",
                parse_mode='HTML'
            )

            # Выполняем первый запрос на ЦИАН для проверки количества
            await _show_initial_search_results(callback, filter_obj, state)

        except Exception as e:
            logger.error(f"Error saving filter for user {callback.from_user.id}: {e}")
            await callback.message.edit_text(
                "❌ Произошла ошибка при сохранении фильтра. Попробуйте еще раз."
            )
            await callback.answer("❌ Ошибка сохранения")

    await callback.answer()


async def _show_initial_search_results(callback: CallbackQuery, filter_obj, state: FSMContext):
    """Показать результаты первичного поиска без сохранения объявлений"""
    from app.db.session import sessionmaker
    from app.db.cruds import RealtyFilterCRUD, OfferCRUD, NotificationCRUD
    
    try:
        # Создаем клиент ЦИАН
        cian_client = CianClient()
        
        # Выполняем поиск
        offers = await cian_client.get_offers(filter_obj)
        
        # Сохраняем существующие объявления в базу и создаем уведомления о них
        if offers:
            async with sessionmaker() as session:
                offer_crud = OfferCRUD(session)
                filter_crud = RealtyFilterCRUD(session)
                notification_crud = NotificationCRUD(session)
                
                # Сохраняем только те объявления, которых еще нет в базе
                offers_to_save = []
                for offer in offers:
                    if not await offer_crud.offer_exists(offer.offer_id):
                        offers_to_save.append(offer)
                
                if offers_to_save:
                    await offer_crud.bulk_create_offers(offers_to_save)
                    logger.info(f"Saved {len(offers_to_save)} existing offers for user {callback.from_user.id}")
                
                # Создаем уведомления о всех найденных объявлениях (чтобы они не показывались повторно)
                notifications_data = []
                for offer in offers:
                    if not await notification_crud.notification_exists(callback.from_user.id, offer.offer_id):
                        notifications_data.append({
                            'user_id': callback.from_user.id,
                            'offer_id': offer.offer_id
                        })
                
                if notifications_data:
                    await notification_crud.bulk_create_notifications(notifications_data)
                    logger.info(f"Created {len(notifications_data)} initial notifications for user {callback.from_user.id} (marked as existing)")
                
                # Помечаем что первичная проверка завершена
                await filter_crud.mark_initial_check_completed(callback.from_user.id)
        
        # Показываем только количество найденных объявлений
        if offers:
            message_text = (
                f"✅ <b>Фильтр успешно сохранен!</b>\n\n"
                f"🔍 <b>Найдено объявлений:</b> {len(offers)}\n"
                #f"🔗 <a href=''>Смотреть объявления на ЦИАН</a>\n\n"
                f"📬 Вы будете получать уведомления о <b>новых</b> объявлениях, "
                f"которые появятся после создания фильтра."
            )
        else:
            message_text = (
                "✅ <b>Фильтр успешно сохранен!</b>\n\n"
                "🔍 <b>Объявления по вашим критериям не найдены.</b>\n"
                "⚠️ <b>Возможно, вы задали слишком строгие критерии поиска.</b>\n\n"
                "📬 Вы будете получать уведомления, как только появятся подходящие объявления."
            )
        
        await callback.message.edit_text(
            message_text,
            parse_mode='HTML'
        )
        
        await state.clear()
        await callback.answer("✅ Фильтр сохранен!")
        
    except Exception as e:
        logger.error(f"Error checking initial offers for user {callback.from_user.id}: {e}")
        
        # Показываем сообщение об успехе даже если поиск не удался
        await callback.message.edit_text(
            "✅ <b>Фильтр успешно сохранен!</b>\n\n"
            "📬 Вы будете получать уведомления о новых объявлениях, "
            "соответствующих вашим критериям.",
            parse_mode='HTML'
        )
        await state.clear()
        await callback.answer("✅ Фильтр сохранен!")