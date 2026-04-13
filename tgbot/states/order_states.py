from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    """FSM состояния для работы с заказами"""
    waiting_for_order_id = State()
    waiting_for_status_order_id = State()
    waiting_for_new_status = State()
