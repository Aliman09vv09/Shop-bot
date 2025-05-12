from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, ContentType
from loader import dp, db
from states.payment_state import PaymentState

@dp.message_handler(state=PaymentState.method)
async def choose_payment_method(message: Message, state: FSMContext):
    if message.text == "Bank Transfer":
        await PaymentState.receipt.set()
        await message.answer("Please upload a screenshot of your bank transfer receipt.")
    elif message.text == "Crypto (TRX/USDT)":
        await PaymentState.tx_hash.set()
        await message.answer("Please enter your transaction hash (TX).")
    else:
        await message.answer("Invalid option. Choose 'Bank Transfer' or 'Crypto (TRX/USDT)'.")

@dp.message_handler(content_types=ContentType.PHOTO, state=PaymentState.receipt)
async def handle_receipt(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    async with state.proxy() as data:
        data['payment_method'] = "Bank Transfer"
        data['payment_data'] = file_id
        data['status'] = "Pending"
        # Save to DB
        db.query('UPDATE orders SET payment_method=?, payment_data=?, status=? WHERE cid=?',
                 (data['payment_method'], data['payment_data'], data['status'], message.chat.id))
    await message.answer("Receipt uploaded. Your order is now pending admin approval.")
    await state.finish()

@dp.message_handler(state=PaymentState.tx_hash)
async def handle_tx_hash(message: Message, state: FSMContext):
    tx_hash = message.text
    async with state.proxy() as data:
        data['payment_method'] = "Crypto"
        data['payment_data'] = tx_hash
        data['status'] = "Pending"
        # Save to DB
        db.query('UPDATE orders SET payment_method=?, payment_data=?, status=? WHERE cid=?',
                 (data['payment_method'], data['payment_data'], data['status'], message.chat.id))
    await message.answer("Transaction hash received. Your order is now pending admin approval.")
    await state.finish()