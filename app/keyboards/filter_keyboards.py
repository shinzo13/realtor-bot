from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.db.enums import Renovation


def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]])

def realty_type_kb():
    """Клавиатура выбора типа жилья"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 Квартира", callback_data="realty_flat")],
        [InlineKeyboardButton(text="🏠 Дом", callback_data="realty_house")],
    ])


def apartment_value_kb():
    """Клавиатура выбора типа квартир (апартаменты или обычные)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Обычные квартиры", callback_data="apartment_no")],
        [InlineKeyboardButton(text="🏢 Апартаменты", callback_data="apartment_yes")],
        # [InlineKeyboardButton(text="📄 Любые", callback_data="apartment_any")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])


def room_count_kb(selected_rooms=None):
    """Клавиатура выбора количества комнат с возможностью множественного выбора"""
    if selected_rooms is None:
        selected_rooms = set()

    keyboard = []

    studio_text = "✅ Студия" if 9 in selected_rooms else "Студия"
    keyboard.append([InlineKeyboardButton(text=studio_text, callback_data="room_9")])

    row2 = []
    for rooms in range(1,6):
        text = f"✅ {rooms}" if rooms in selected_rooms else str(rooms)
        row2.append(InlineKeyboardButton(text=text, callback_data=f"room_{rooms}"))

    keyboard.append(row2)

    row3 = [InlineKeyboardButton(text="⬅️ Назад", callback_data="back"),
            InlineKeyboardButton(text="Дальше ➡️", callback_data="rooms_confirm")]

    keyboard.append(row3)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def search_address_kb():
    """Клавиатура для поиска адреса"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📍 Выбрать адрес", switch_inline_query_current_chat="")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])


def price_range_kb():
    """Клавиатура выбора ценового диапазона"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Неважно", callback_data="price_any")
        ],
        [
            InlineKeyboardButton(text="До 30к", callback_data="price_0_30000"),
            InlineKeyboardButton(text="30-50к", callback_data="price_30000_50000")
        ],
        [
            InlineKeyboardButton(text="50-80к", callback_data="price_50000_80000"),
            InlineKeyboardButton(text="80-120к", callback_data="price_80000_120000")
        ],
        [
            InlineKeyboardButton(text="120к+", callback_data="price_120000_0"),
            InlineKeyboardButton(text="💰 Свой диапазон", callback_data="price_custom")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
        ]
    ])


def other_filters_kb(selected_other_filters=None):
    if selected_other_filters is None:
        selected_other_filters = set()
    other_filters = {
        "kids": "С детьми",
        "pets": "С животными",
        "no_deposit": "Без залога"
    }

    keyboard = []

    # Добавляем кнопки для каждого типа ремонта
    for renovation, name in other_filters.items():
        text = f"✅ {name}" if renovation in selected_other_filters else name
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"other_{renovation}")])

    # Кнопки управления
    control_buttons = [
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back"),
        InlineKeyboardButton(text="Дальше ➡️", callback_data="other_confirm")
    ]
    keyboard.append(control_buttons)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def renovation_kb(selected_renovations=None):
    """Клавиатура выбора типов ремонта с множественным выбором"""
    if selected_renovations is None:
        selected_renovations = set()

    renovation_names = {
        "any": "Неважно",
        "cosmetic": "Косметический",
        "euro": "Евроремонт",
        "designed": "Дизайнерский"
    }

    keyboard = []

    # Добавляем кнопки для каждого типа ремонта
    for renovation, name in renovation_names.items():
        text = f"✅ {name}" if renovation in selected_renovations else name
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"renovation_{renovation}")])

    # Кнопки управления
    control_buttons = [InlineKeyboardButton(text="⬅️ Назад", callback_data="back"),
                       InlineKeyboardButton(text="Дальше ➡️", callback_data="renovation_confirm")]
    keyboard.append(control_buttons)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# def keywords_kb():
#     """Клавиатура для ввода ключевых слов"""
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="⏭️ Пропустить", callback_data="keywords_skip")],
#         [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_renovation")]
#     ])


def confirm_filter_kb():
    """Клавиатура подтверждения фильтра"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back"),
            InlineKeyboardButton(text="✅ Сохранить фильтр", callback_data="filter_save")
        ],
#        [InlineKeyboardButton(text="❌ Отменить", callback_data="filter_cancel")]
    ])

#
# def edit_filter_kb():
#     """Клавиатура для редактирования фильтра"""
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [
#             InlineKeyboardButton(text="🏠 Тип жилья", callback_data="edit_building_type"),
#             InlineKeyboardButton(text="🏢 Апартаменты", callback_data="edit_apartment_type")
#         ],
#         [
#             InlineKeyboardButton(text="🔢 Комнаты", callback_data="edit_rooms"),
#             InlineKeyboardButton(text="📍 Адрес", callback_data="edit_address")
#         ],
#         [
#             InlineKeyboardButton(text="💰 Цена", callback_data="edit_price"),
#             InlineKeyboardButton(text="💳 Залог", callback_data="edit_deposit")
#         ],
#         [
#             InlineKeyboardButton(text="👶 Дети", callback_data="edit_kids"),
#             InlineKeyboardButton(text="🐕 Животные", callback_data="edit_pets")
#         ],
#         [
#             InlineKeyboardButton(text="🔨 Ремонт", callback_data="edit_renovation"),
#             InlineKeyboardButton(text="🔍 Ключевые слова", callback_data="edit_keywords")
#         ],
#         [InlineKeyboardButton(text="⬅️ Назад к подтверждению", callback_data="back_to_confirm")]
#     ])