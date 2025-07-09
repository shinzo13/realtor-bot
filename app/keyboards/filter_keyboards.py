from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def building_status_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Новостройка", callback_data="status_new")],
        [InlineKeyboardButton(text="Вторичка", callback_data="status_old")],
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