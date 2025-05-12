import logging
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from handlers.user.catalog import process_catalog
from loader import dp

# Admin Handlers
@dp.callback_query_handler(lambda c: c.data == 'admin_manage_products')
async def admin_manage_products(callback_query: CallbackQuery):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🔙 Back", callback_data="role_admin")  # Back to Admin Menu
    )
    await callback_query.message.edit_text("🛠 Manage Products functionality is not yet implemented.", reply_markup=markup)
    await callback_query.answer()  # Toast notification (no additional message)

@dp.callback_query_handler(lambda c: c.data == 'admin_view_orders')
async def admin_view_orders(callback_query: CallbackQuery):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🔙 Back", callback_data="role_admin")  # Back to Admin Menu
    )
    await callback_query.message.edit_text("📦 View Orders functionality is not yet implemented.", reply_markup=markup)
    await callback_query.answer()  # Toast notification (no additional message)

# Customer Handlers
@dp.callback_query_handler(lambda c: c.data == 'customer_catalog')
async def customer_catalog(callback_query: CallbackQuery):
    # Call the existing catalog logic
    await process_catalog(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == 'customer_view_cart')
async def customer_view_cart(callback_query: CallbackQuery):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🔙 Back", callback_data="role_customer")  # Back to Customer Menu
    )
    await callback_query.message.edit_text("🛒 View Cart functionality is not yet implemented.", reply_markup=markup)
    await callback_query.answer()  # Toast notification (no additional message)

