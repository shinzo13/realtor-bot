from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.callback_data import CallbackData
from app.db.enums import RealtyType


class SetupRealtyFilterForm(StatesGroup):
    choosing_realty_type = State()        # Тип жилья: квартира/дом
    choosing_apartment_value = State()    # Апартаменты: да/нет (только для квартир)
    choosing_rooms = State()              # Количество комнат (только для квартир)
    entering_address = State()            # Адрес
    entering_price_range = State()        # Ценовой диапазон
    entering_custom_min_price = State()
    entering_custom_max_price = State()
    choosing_other = State()              # залог дети животные
    choosing_renovation = State()         # Тип ремонта
    entering_keywords = State()           # Ключевые слова (потом)
    confirming_filter = State()           # Подтверждение фильтра

# class SetupRealtyFilterCallback(CallbackData, prefix="rt"):
#     confirmed: bool # это АХУЕННЫЙ костыль я ГЕНИЙ
#
#     realty_type: RealtyType
#     apartment: bool
#     rooms: list[int]
#     price_range: tuple[int, int]
#     other: dict[str, bool]
#     renovation: dict[str, bool]

