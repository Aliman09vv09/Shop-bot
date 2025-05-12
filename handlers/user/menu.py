
import logging
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from keyboards.inline.categories import categories_markup
from loader import dp
from filters import IsAdmin, IsUser
from utils import db

catalog = '🛍️ Каталог'
balance = '💰 Баланс'
cart = '🛒 Корзина'
delivery_status = '🚚 Статус заказа'

settings = '⚙️ Настройка каталога'
orders = '🚚 Заказы'
questions = '❓ Вопросы'

@dp.message_handler(IsAdmin(), commands='menu')
async def admin_menu(message: Message):
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(settings)
    markup.add(questions, orders)

    await message.answer('Меню', reply_markup=markup)

@dp.message_handler(IsUser(), commands='menu')
async def user_menu(message: Message):
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(catalog)
    markup.add(balance, cart)
    markup.add(delivery_status)

    await message.answer('Menu', reply_markup=markup)

@dp.message_handler(IsUser(), text='🛍️ Каталог')
async def process_catalog(message: Message):
    categories = db.fetchall('SELECT * FROM categories')
    if not categories:
        await message.answer("No categories available at the moment.")
        return
    await message.answer('Choose a category to view products:', reply_markup=categories_markup())