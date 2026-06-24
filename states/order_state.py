from aiogram.fsm.state import StatesGroup,State
class OrderState(StatesGroup):
    waiting_link=State()
    waiting_quantity=State()
