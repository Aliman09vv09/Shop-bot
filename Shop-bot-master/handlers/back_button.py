from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp
from data import config  # Assume this contains a list of admin IDs
import logging

@dp.callback_query_handler(lambda c: c.data == 'back_to_start')
async def back_to_role_selection(callback_query):
    # Log that the handler was triggered
    logging.info(f"Back to start triggered by user {callback_query.from_user.id}")
    print(f"[DEBUG] Back to start triggered by user {callback_query.from_user.id}")

    # Ensure only admins can access the role selection menu
    if callback_query.from_user.id not in config.ADMINS:
        try:
            # Log the restricted access attempt
            logging.info(f"Non-admin user {callback_query.from_user.id} tried to access the role selection menu.")
            print(f"[DEBUG] Non-admin user {callback_query.from_user.id} tried to access the role selection menu.")
            await callback_query.answer("Customers cannot access this menu!", show_alert=True)  # Alert notification
        except Exception as e:
            # Log any exceptions
            logging.error(f"Error sending toast notification for restricted access: {e}")
            print(f"[DEBUG] Error sending toast notification for restricted access: {e}")
        return

    # Inline keyboard for Role Selection
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("👨‍💼 Admin", callback_data="role_admin"),
        InlineKeyboardButton("👤 Customer", callback_data="role_customer")
    )

    try:
        # Update the message with the role selection menu
        logging.info("Navigating back to the role selection menu.")
        print("[DEBUG] Navigating back to the role selection menu.")
        await callback_query.message.edit_text("Welcome! Please choose your role:", reply_markup=markup)
        # Provide subtle toast notification
        await callback_query.answer("Returning to role selection...", show_alert=False)
    except Exception as e:
        # Handle cases where the message cannot be edited (e.g., it was deleted)
        logging.error(f"Error navigating back to role selection: {e}")
        print(f"[DEBUG] Error navigating back to role selection: {e}")
        await callback_query.answer("Unable to go back. Please press /start.", show_alert=True)