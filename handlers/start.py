from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp
from data import config  # Assume this contains a list of admin IDs

@dp.message_handler(commands=['start'])
async def start(message):
    if message.from_user.id in config.ADMINS:  # Check if the user is an admin
        # Inline Keyboard for Role Selection
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("👤 Customer", callback_data="role_customer"),
            InlineKeyboardButton("👨‍💼 Admin", callback_data="role_admin")
        )
        await message.answer("Welcome! Please choose your role:", reply_markup=markup)
    else:
        # Non-admins go directly to the Customer role
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🛍️ Catalog", callback_data="customer_catalog"),
            InlineKeyboardButton("🛒 View Cart", callback_data="customer_view_cart")
        )
        await message.answer("Welcome to the Customer menu!", reply_markup=markup)