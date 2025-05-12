from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from loader import dp
from data import config  # Assume this contains a list of admin IDs

# Admin Role Handler
@dp.callback_query_handler(lambda c: c.data == 'role_admin')
async def select_admin_role(callback_query):
    # Restrict access to admin menu
    if callback_query.from_user.id not in config.ADMINS:
        await callback_query.answer("You are not authorized to access the admin menu!", show_alert=True)  # Alert for restricted access
        return

    # Inline keyboard for admin-specific options
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("⚙️ Manage Products", callback_data="admin_manage_products"),
        InlineKeyboardButton("📦 View Orders", callback_data="admin_view_orders"),
        InlineKeyboardButton("🔙 Back", callback_data="back_to_start")  # Back Button
    )

    await callback_query.message.edit_text("You've selected Admin. Choose an option:", reply_markup=markup)
    await callback_query.answer("Admin menu loaded.", show_alert=False)  # Toast notification

# Customer Role Handler
@dp.callback_query_handler(lambda c: c.data == 'role_customer')
async def select_customer_role(callback_query):
    # Inline keyboard for customer-specific options
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🛍️ Catalog", callback_data="customer_catalog"),
        InlineKeyboardButton("🛒 View Cart", callback_data="customer_view_cart")
    )

    # Add "Back" button only if the user is an admin
    if callback_query.from_user.id in config.ADMINS:
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="back_to_start"))

    await callback_query.message.edit_text("You've selected Customer. Choose an option:", reply_markup=markup)
    await callback_query.answer()  # Toast notification (no additional message)