import os
import handlers
from aiogram import executor, types
from aiogram.types import ReplyKeyboardRemove
from data import config
from loader import dp, db, bot
import filters
import logging
import handlers.start  # Import the start handler
import handlers.role_selection  # Import the role selection handler
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp  # Ensure this imports the dispatcher correctly
import handlers.start
import handlers.role_selection
import handlers.role_actions

filters.setup(dp)

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 5000))
user_message = 'Пользователь'
admin_message = 'Админ'


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Inline Keyboard for Role Selection
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("👨‍💼 Admin", callback_data="role_admin"),
        InlineKeyboardButton("👤 Customer", callback_data="role_customer")
    )
    await message.answer("Welcome! Please choose your role:", reply_markup=markup)


@dp.message_handler(text=user_message)
async def user_mode(message: types.Message):

    cid = message.chat.id
    if cid in config.ADMINS:
        config.ADMINS.remove(cid)

    await message.answer('حالت کاربری فعال است.', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(text=admin_message)
async def admin_mode(message: types.Message):

    cid = message.chat.id
    if cid not in config.ADMINS:
        config.ADMINS.append(cid)

    await message.answer('حالت مدیریت فعال است.', reply_markup=ReplyKeyboardRemove())


async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)
    db.create_tables()

    await bot.delete_webhook()
    if config.WEBHOOK_URL:
        await bot.set_webhook(config.WEBHOOK_URL)


async def on_shutdown():
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bot down")


if __name__ == '__main__':

    if (("HEROKU_APP_NAME" in list(os.environ.keys())) or
        ("RAILWAY_PUBLIC_DOMAIN" in list(os.environ.keys()))):

        executor.start_webhook(
            dispatcher=dp,
            webhook_path=config.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )

    else:

        executor.start_polling(dp, on_startup=on_startup, skip_updates=False)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
