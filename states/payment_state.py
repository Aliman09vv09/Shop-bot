from aiogram.dispatcher.filters.state import StatesGroup, State

class PaymentState(StatesGroup):
    method = State()
    receipt = State()
    tx_hash = State()