from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from utils.db import create_order, clear_cart

@dp.message_handler(commands=["checkout"])
async def checkout(message: types.Message, state: FSMContext):
    total = calculate_total(user_id=message.from_user.id)
    if total == 0:
        await message.answer("Your cart is empty!")
        return

    await message.answer(f"Your total is ${total:.2f}. Please choose a payment method:\n1️⃣ Bank Transfer\n2️⃣ Crypto (TRX/USDT)")
    # Simulate order creation
    create_order(user_id=message.from_user.id, total=total)
    clear_cart(user_id=message.from_user.id)