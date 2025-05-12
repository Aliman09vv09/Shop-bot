from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from utils.db import get_cart, add_to_cart, remove_from_cart, calculate_total

@dp.message_handler(commands=["view_cart"])
async def view_cart(message: types.Message, state: FSMContext):
    cart = get_cart(user_id=message.from_user.id)
    if not cart:
        await message.answer("Your cart is empty!")
        return

    response = "🛒 **Your Cart:**\n"
    for item in cart:
        response += f"- {item['title']} (${item['price']:.2f})\n"
    response += f"\n**Total:** ${calculate_total(user_id=message.from_user.id):.2f}"
    await message.answer(response)

@dp.callback_query_handler(lambda c: c.data.startswith("add_to_cart"))
async def add_to_cart_handler(callback_query: types.CallbackQuery):
    service_id = int(callback_query.data.split(":")[1])
    add_to_cart(user_id=callback_query.from_user.id, service_id=service_id)
    await callback_query.answer("Item added to your cart!")

@dp.callback_query_handler(lambda c: c.data.startswith("remove_from_cart"))
async def remove_from_cart_handler(callback_query: types.CallbackQuery):
    service_id = int(callback_query.data.split(":")[1])
    remove_from_cart(user_id=callback_query.from_user.id, service_id=service_id)
    await callback_query.answer("Item removed from your cart!")