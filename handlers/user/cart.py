import logging
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.products_from_cart import product_markup, product_cb
from aiogram.utils.callback_data import CallbackData
from aiogram.types.chat import ChatActions
from loader import dp, db, bot
from filters import IsUser
from states import CheckoutState
from keyboards.default.markups import *
from .menu import cart
from states.payment_state import PaymentState


@dp.message_handler(IsUser(), text="🛒 View Cart")
async def process_cart(message: Message, state: FSMContext):
    cart_data = db.fetchall('SELECT * FROM cart WHERE cid=?', (message.chat.id,))
    if len(cart_data) == 0:
        await message.answer("Your cart is empty.")
    else:
        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        async with state.proxy() as data:
            data['products'] = {}

        order_cost = 0
        for _, idx, count_in_cart in cart_data:
            product = db.fetchone('SELECT * FROM products WHERE idx=?', (idx,))
            if product is None:
                db.query('DELETE FROM cart WHERE idx=?', (idx,))
            else:
                _, title, body, image, price, _ = product
                order_cost += price * count_in_cart
                async with state.proxy() as data:
                    data['products'][idx] = [title, price, count_in_cart]

                markup = product_markup(idx, count_in_cart)
                text = f'<b>{title}</b>\n\n{body}\n\nPrice: {price} IRR x {count_in_cart} = {price * count_in_cart} IRR'

                await message.answer_photo(photo=image, caption=text, reply_markup=markup)

        if order_cost != 0:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("📦 Proceed to Checkout")
            await message.answer(f'Total Cost: {order_cost} IRR\n\nProceed to checkout?', reply_markup=markup)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='count'))
@dp.callback_query_handler(IsUser(), product_cb.filter(action='increase'))
@dp.callback_query_handler(IsUser(), product_cb.filter(action='decrease'))
async def product_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    idx = callback_data['id']
    action = callback_data['action']

    if 'count' == action:
        async with state.proxy() as data:
            if 'products' not in data.keys():
                await process_cart(query.message, state)
            else:
                count_in_cart = data['products'][idx][2]
                await query.answer(f"Quantity: {count_in_cart}")
    else:
        async with state.proxy() as data:
            if 'products' not in data.keys():
                await process_cart(query.message, state)
            else:
                data['products'][idx][2] += 1 if 'increase' == action else -1
                count_in_cart = data['products'][idx][2]

                if count_in_cart == 0:
                    db.query('DELETE FROM cart WHERE cid=? AND idx=?', (query.message.chat.id, idx))
                    await query.message.delete()
                else:
                    db.query('UPDATE cart SET quantity=? WHERE cid=? AND idx=?',
                             (count_in_cart, query.message.chat.id, idx))
                    await query.message.edit_reply_markup(product_markup(idx, count_in_cart))


@dp.message_handler(IsUser(), text="📦 Proceed to Checkout")
async def process_checkout(message: Message, state: FSMContext):
    await CheckoutState.check_cart.set()
    await checkout(message, state)


async def checkout(message, state):
    async with state.proxy() as data:
        answer = ''
        total_price = 0
        for title, price, count_in_cart in data['products'].values():
            tp = count_in_cart * price
            answer += f'<b>{title}</b> x {count_in_cart} = {tp} IRR\n'
            total_price += tp

        await message.answer(f"Your Order:\n\n{answer}\nTotal: {total_price} IRR\n\nPlease proceed to payment.",
                             reply_markup=ReplyKeyboardRemove())
    await state.finish()
    

@dp.message_handler(IsUser(), text="🛒 Proceed to Payment")
async def process_payment(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Bank Transfer", "Crypto (TRX/USDT)")
    await PaymentState.method.set()
    await message.answer("Choose a payment method:", reply_markup=markup)


@dp.message_handler(IsUser(), lambda message: message.text not in [all_right_message, back_message], state=CheckoutState.check_cart)
async def process_check_cart_invalid(message: Message):
    await message.reply('Такого варианта не было.')


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.check_cart)
async def process_check_cart_back(message: Message, state: FSMContext):
    await state.finish()
    await process_cart(message, state)


@dp.message_handler(IsUser(), text=all_right_message, state=CheckoutState.check_cart)
async def process_check_cart_all_right(message: Message, state: FSMContext):
    await CheckoutState.next()
    await message.answer('Укажите свое имя.',
                         reply_markup=back_markup())


@dp.message_handler(IsUser(), lambda message: message.text not in [confirm_message, back_message], state=CheckoutState.confirm)
async def process_confirm_invalid(message: Message):
    await message.reply('Такого варианта не было.')


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):

    await CheckoutState.address.set()

    async with state.proxy() as data:
        await message.answer('Изменить адрес с <b>' + data['address'] + '</b>?',
                             reply_markup=back_markup())


@dp.message_handler(IsUser(), text=confirm_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    markup = ReplyKeyboardRemove()

    async with state.proxy() as data:
        cid = message.chat.id
        products = [idx + '=' + str(quantity)
                    for idx, quantity in db.fetchall('''SELECT idx, quantity FROM cart
            WHERE cid=?''', (cid,))]  # idx=quantity

        # Ensure all 7 columns are handled in the INSERT query
        db.query('INSERT INTO orders (cid, usr_name, usr_address, products, payment_method, payment_data, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (
                     cid,
                     data.get('name', ''),  # Optional, default to empty if not provided
                     data.get('address', ''),  # Optional, default to empty if not provided
                     ' '.join(products),
                     None,  # payment_method (initially NULL)
                     None,  # payment_data (initially NULL)
                     'Pending'  # status (default to 'Pending')
                 ))

        # Clear the cart after order placement
        db.query('DELETE FROM cart WHERE cid=?', (cid,))

        await message.answer('✅ Your order has been placed! 🚀', reply_markup=markup)
    await CheckoutState.confirm.set()
    await message.answer('Please confirm your order:', reply_markup=confirm_markup())

    await state.finish()
