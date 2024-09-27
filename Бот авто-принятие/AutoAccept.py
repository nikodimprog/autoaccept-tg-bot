from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import Database
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import asyncio
import aiogram

bot = Bot(token="1234567890:AAKvIlbE5zo5_aq1yNe-0jgCmgSKfiMsdgDc", parse_mode='HTML')
admin_id = 123456789
group_id = -1201456669786
channelid = -10018166123577

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database()

remove_keyboard_markup = types.ReplyKeyboardRemove()

class UserConfirmation(StatesGroup):
    confirmation = State()

@dp.chat_join_request_handler()
async def start1(update: types.ChatJoinRequest):
    confirm_button = KeyboardButton('Подтвердить')
    reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(confirm_button)
    await bot.send_message(chat_id=admin_id, text=f"<b>➕ Новая заявка в канал: </b> @{update.from_user.username} [<code>{update.from_user.id}</code>]")
    await update.bot.send_message(chat_id=update.from_user.id, text=f'<b>‼️ {update.from_user.full_name}, для доступа к каналу нажми кнопку <u>"Подтвердить"</u></b>', reply_markup=reply_keyboard)
    state = dp.current_state(user=update.from_user.id)
    await state.set_state(UserConfirmation.confirmation)

@dp.message_handler(content_types=types.ContentType.TEXT, text=['Подтвердить'])
async def confirm_user(message: types.Message, state: FSMContext):
    await bot.approve_chat_join_request(chat_id=channelid, user_id=message.from_user.id)
    usersf = db.get_user(message.from_user.id)
    if usersf is not None:
        db.add_user(message.from_user.id)
        await bot.send_message(chat_id=admin_id, text=f"<b>✅ Приняли в канал пользователя:</b> @{message.from_user.username} [<code>{message.from_user.id}</code>]")
        await message.answer(f'<b>✅ {message.from_user.full_name} твоя <u>заявка</u> в канал была <u>прията</u>!\n\n☁️ Автор - WHSoft Cloud / https://t.me/+hDc6HaNkf5Q3NzNi \n\n Распространил CONFF.ORG.\n\n⚠️ Для получения актуальной ссылки в случаи блокировки, пропиши <u>/start</u></b>', disable_web_page_preview=True, reply_markup=remove_keyboard_markup)
        await state.finish()
    else:
        await message.answer(f'<b>✅ {message.from_user.full_name} твоя <u>заявка</u> в канал была <u>прията</u>!\n\n☁️ Автор - WHSoft Cloud / https://t.me/+hDc6HaNkf5Q3NzNi \n\n Распространил CONFF.ORG.\n\n⚠️ Для получения актуальной ссылки в случаи блокировки, пропиши <u>/start</u></b>', disable_web_page_preview=True, reply_markup=remove_keyboard_markup)
        await bot.send_message(chat_id=admin_id, text=f"<b>✅Приняли в канал пользователя:</b> @{message.from_user.username} [<code>{message.from_user.id}</code>]")
        await state.finish()


@dp.message_handler(state=UserConfirmation.confirmation)
async def handle_confirmation(message: types.Message,state=FSMContext):
    print(state)
    await message.answer('<b>⚠️ Для доступа к каналу нажми кнопку <u>"Подтвердить"</u></b>')

#######################################################

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    existing_user = db.get_user(message.from_user.id)
    if existing_user is not None:
        await message.answer("💰")
        await message.answer("<b>Привет, @{message.from_user.username}.\nБольше разных сливов заработка - https://t.me/+7xF6Jb3ka9A0ZDhi</b>", disable_web_page_preview=True, reply_markup=remove_keyboard_markup)
    else:
        await message.answer("💰")
        await message.answer("<b>Привет, @{message.from_user.username}.\nБольше разных сливов заработка - https://t.me/+7xF6Jb3ka9A0ZDhi</b>", disable_web_page_preview=True, reply_markup=remove_keyboard_markup)
        db.add_user(message.from_user.id)

@dp.message_handler(content_types="new_chat_members")
async def on_user_join(message: types.Message):
    await message.delete()
    await bot.send_message(chat_id=admin_id, text=f'✅ Новый участник в чате:\n\n'
                                               f'{message.from_user.get_mention()} | {message.from_user.full_name}\n'
                                               f'Id: {message.from_user.id}\n'
                                               f'Username: @{message.from_user.username}\n'
                                               )
    new_msg = await message.answer(f'{message.from_user.get_mention()} добро пожаловать в чат!', disable_web_page_preview=True)
    await asyncio.sleep(15)
    try:
        await new_msg.delete()
    except Exception as e:
        pass

@dp.message_handler(content_types="left_chat_member")
async def on_user_join(message: types.Message):
    await message.delete()

@dp.message_handler(content_types="new_chat_title")
async def on_user_join(message: types.Message):
    await message.delete()

@dp.message_handler(content_types="new_chat_photo")
async def on_user_join(message: types.Message):
    await message.delete()

@dp.message_handler(content_types="delete_chat_photo")
async def on_user_join(message: types.Message):
    await message.delete()

@dp.message_handler(commands=['send_all'])
async def send_all_users(message: types.Message):
    if message.from_user.id == admin_id:
        users = db.get_users()
        successful_sends = 0
        failed_sends = 0
        for user in users:
            try:
                await bot.send_message(chat_id=user[0], text=message.text.replace("/send_all ", ""))
                await asyncio.sleep(0.5)
                successful_sends += 1
            except aiogram.utils.exceptions.TelegramAPIError as e:
                failed_sends += 1
        await bot.send_message(chat_id=admin_id, text=f"Рассылка завершена!\n\nУспешно отправлено сообщений: {successful_sends}\nСообщений с ошибками: {failed_sends}")

@dp.message_handler(content_types=['photo', 'video', 'document', 'text'], chat_id=group_id)
async def handle_comment(message: types.Message):
    if message.from_user.id != 777000:
        pass
    elif message.chat.id != group_id:
        pass
    else:
        await message.reply("+", disable_web_page_preview=True)

if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    finally:
        db.close()