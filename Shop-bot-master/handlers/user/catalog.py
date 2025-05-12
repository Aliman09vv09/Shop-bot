import logging
from aiogram.types import Message, CallbackQuery
from keyboards.inline.categories import categories_markup, category_cb
from keyboards.inline.products_from_catalog import product_markup, product_cb
from aiogram.utils.callback_data import CallbackData
from aiogram.types.chat import ChatActions
from loader import dp, db, bot
from .menu import catalog
from filters import IsUser


@dp.message_handler(IsUser(), text='🛍️ Каталог')
async def process_catalog(message: Message):
    categories = db.fetchall('SELECT * FROM categories')  # Ensure categories are fetched
    if not categories:
        await message.answer("No categories available at the moment.")
        return
    await message.answer('Choose a category to view products:', reply_markup=categories_markup())


@dp.callback_query_handler(IsUser(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict):
    products = db.fetchall('''SELECT * FROM products WHERE tag = (
        SELECT title FROM categories WHERE idx = ?)''', (callback_data['id'],))

    if not products:
        await query.answer("No products found in this category.", show_alert=True)
        return

    await query.answer('Displaying products...')
    await show_products(query.message, products)

@dp.callback_query_handler(IsUser(), category_cb.filter(action='view'))
async def customer_category_callback_handler(query: CallbackQuery, callback_data: dict):
    # Fetch the category index
    category_idx = callback_data['id']
    
    # Fetch products linked to this category
    products = db.fetchall('SELECT * FROM products WHERE tag = (SELECT title FROM categories WHERE idx=?)', (category_idx,))
    
    if not products:
        await query.answer("No products found in this category.", show_alert=True)
        return

    # Display products to the customer
    await query.answer('Displaying products...')
    for product in products:
        idx, title, body, image, price, tag = product
        await query.message.answer_photo(
            photo=image,
            caption=f"<b>{title}</b>\n\n{body}\n\nPrice: {price} IRR\n\nCategory: {tag}",
        )


@dp.callback_query_handler(IsUser(), product_cb.filter(action='add'))
async def add_product_callback_handler(query: CallbackQuery, callback_data: dict):

    db.query('INSERT INTO cart VALUES (?, ?, 1)',
             (query.message.chat.id, callback_data['id']))

    await query.answer('Товар добавлен в корзину!')
    await query.message.delete()


async def show_products(m, products):
    if len(products) == 0:
        await m.answer('No products available in this category 😢')
    else:
        await bot.send_chat_action(m.chat.id, ChatActions.TYPING)
        for idx, title, body, image, price, _ in products:
            markup = product_markup(idx, price)
            text = f"<b>{title}</b>\n\n{body}\n\nPrice: {price}₽"
            
            # Send each product with its inline keyboard
            await m.answer_photo(photo=image, caption=text, reply_markup=markup)
