from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def building_status_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 Квартира", callback_data="status_flat")],
        [InlineKeyboardButton(text="🏠 Дом", callback_data="status_house")],
    ])

def room_count_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1", callback_data="room_1"),
            InlineKeyboardButton(text="2", callback_data="room_2"),
            InlineKeyboardButton(text="3", callback_data="room_3")
        ],
        [
            InlineKeyboardButton(text="4", callback_data="room_4"),
            InlineKeyboardButton(text="5", callback_data="room_5"),
            InlineKeyboardButton(text="6+", callback_data="room_6")
        ]
    ])

def search_address_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="📍 Выбрать адрес",
            switch_inline_query_current_chat=""
        )
    ]])

def price_range_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="До 30к", callback_data="price_0_30000"),
            InlineKeyboardButton(text="30-50к", callback_data="price_30000_50000")
        ],
        [
            InlineKeyboardButton(text="50-80к", callback_data="price_50000_80000"),
            InlineKeyboardButton(text="80к+", callback_data="price_80000_0")
        ],
        [
            InlineKeyboardButton(text="Указать свой диапазон", callback_data="price_custom")
        ]
    ])

def yes_no_kb(callback_prefix: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=f"{callback_prefix}_yes"),
            InlineKeyboardButton(text="Нет", callback_data=f"{callback_prefix}_no")
        ]
    ])

def renovation_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Косметический", callback_data="renovation_cosmetic")],
        [InlineKeyboardButton(text="Евроремонт", callback_data="renovation_euro")],
        [InlineKeyboardButton(text="Дизайнерский", callback_data="renovation_designed")],
        [InlineKeyboardButton(text="Неважно", callback_data="renovation_any")],
    ])