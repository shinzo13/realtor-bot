from aiogram.fsm.state import StatesGroup, State

class FilterStates(StatesGroup):
    choosing_building_status = State()
    choosing_rooms = State()
    entering_address = State()