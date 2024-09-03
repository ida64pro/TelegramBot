import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from pymongo import MongoClient
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime

API_TOKEN = 'BOT_TOKEN'

logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

cluster = MongoClient(
    'CLUSTER')
collusers = cluster.Telegram.users
collhomework = cluster.Telegram.homework


class Form(StatesGroup):
    waiting_for_answer = State()
    waiting_for_answer_add_admin = State()

    subject = State()
    hw = State()

    subject_added = ''



async def on_ready():
    me = await bot.get_me()  # Получаем информацию о боте
    logging.info(f"Бот {me.username} ({me.id}) успешно запущен!")
    current_time = datetime.now()
    Form.current_time = current_time


# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    result = collusers.find_one({'access_user_ids': {'id': message.from_user.id}})
    result_time = Form.current_time.strftime('%d.%m.%Y %H:%M:%S')
    if result:
        await message.reply(f"SchoolBot | Бот для получения домашнего задания.\nРазработчик: @skefz\nАдмины: "
                            f"@skefz\nОнлайн с {result_time}.\n\nСписок комманд:\n.Алгебра, .Геометрия, .Химия, "
                            f".Физика, .История, .ОБЖ,"
                            f".Русский, .Английский, .Литература, .Технология, .Биология, .Обществознание, "
                            f".География, /about, /start")
    else:
        await message.reply(f'Go away! (Уходи!) Ваш user_id: {message.from_user.id}')
    await asyncio.sleep(3)
    await message.delete()



@dp.message(Command("admin"))
async def send_admin(message: types.Message):
    result = collusers.find_one({'admin_ids': {'id': message.from_user.id}})
    if result:
        kb = [
            [types.KeyboardButton(text="Добавить юзера в бота")],
            [types.KeyboardButton(text="Добавить админа в бота")],
            [types.KeyboardButton(text="Добавить Д/З")]
        ]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Выберите функцию",
            one_time_keyboard=True
        )
        await message.answer("Что делаем?", reply_markup=keyboard)
    else:
        await message.reply(f'Go away! (Уходи!) Ваш user_id: {message.from_user.id}')
    await asyncio.sleep(5)
    await message.delete()



@dp.message(F.text.lower() == 'добавить юзера в бота')
async def user_add(message: types.Message, state: FSMContext):
    result = collusers.find_one({'admin_ids': {'id': message.from_user.id}})
    if result:
        await message.reply('Введите user_id пользователя, которого хотите занести в базу данных.', reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Form.waiting_for_answer)


@dp.message(Form.waiting_for_answer)
async def handle_response(message: Message, state: FSMContext):
    user_response = message.text
    try:
        user_response = int(user_response)
    except:
        await message.reply('Вы ввели не user_id.')
        return
    result = collusers.find_one({'access_user_ids': {'id': user_response}})
    if result:
        await message.reply('Пользователь уже в БД.')
    else:
        collusers.update_one({'_id': 1}, {'$push': {'access_user_ids': {'id': user_response}}})
        await message.reply('Пользователь добавлен в БД.')

    await state.clear()

@dp.message(F.text.lower() == 'добавить админа в бота')
async def admin_add(message: types.Message, state: FSMContext):
    result = collusers.find_one({'admin_ids': {'id': message.from_user.id}})
    if result:
        await message.reply('Введите user_id пользователя, которого хотите занести в базу данных.', reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Form.waiting_for_answer_add_admin)

@dp.message(Form.waiting_for_answer_add_admin)
async def handle_response_admin(message: Message, state: FSMContext):
    user_response = message.text
    try:
        user_response = int(user_response)
    except:
        await message.reply('Вы ввели не user_id.')
        return
    result = collusers.find_one({'admin_ids': {'id': user_response}})
    if result:
        await message.reply('Пользователь уже в БД.')
    else:
        collusers.update_one({'_id': 1}, {'$push': {'admin_ids': {'id': user_response}}})
        await message.reply('Пользователь добавлен в БД.')

    await state.clear()

@dp.message(F.text.lower() == 'добавить д/з')
async def hw_add(message: types.Message, state: FSMContext):
    result = collusers.find_one({'admin_ids': {'id': message.from_user.id}})
    if result:
        await message.reply('Введите название предмета.',
                            reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Form.subject)

@dp.message(Form.subject)
async def handle_response_admin(message: Message, state: FSMContext):
    user_text = message.text.strip()

    if user_text == "Алгебра":
        await message.reply("Вы выбрали предмет: Алгебра, введите домашнее задание.")
        Form.subject_added = 'Algebry'
    elif user_text == "Геометрия":
        await message.reply("Вы выбрали предмет: Геометрия, введите домашнее задание.")
        Form.subject_added = 'Geometry'
    elif user_text == "Химия":
        await message.reply("Вы выбрали предмет: Химия, введите домашнее задание.")
        Form.subject_added = 'Chemistry'
    elif user_text == "Физика":
        await message.reply("Вы выбрали предмет: Физика, введите домашнее задание.")
        Form.subject_added = 'Physic'
    elif user_text == "История":
        await message.reply("Вы выбрали предмет: История, введите домашнее задание.")
        Form.subject_added = 'History'
    elif user_text == "ОБЖ" or user_text == 'ОБЗР':
        await message.reply("Вы выбрали предмет: ОБЖ, введите домашнее задание.")
        Form.subject_added = 'OBJ'
    elif user_text == "Русский":
        await message.reply("Вы выбрали предмет: Русский, введите домашнее задание.")
        Form.subject_added = 'Russian'
    elif user_text == "Английский":
        await message.reply("Вы выбрали предмет: Английский, введите домашнее задание.")
        Form.subject_added = 'English'
    elif user_text == "Литература":
        await message.reply("Вы выбрали предмет: Литература, введите домашнее задание.")
        Form.subject_added = 'Literature'
    elif user_text == "Технология":
        await message.reply("Вы выбрали предмет: Технология, введите домашнее задание.")
        Form.subject_added = 'Technology'
    elif user_text == "Биология":
        await message.reply("Вы выбрали предмет: , введите домашнее задание.")
        Form.subject_added = 'Biology'
    elif user_text == "Обществознание":
        await message.reply("Вы выбрали предмет: Человековедение, введите домашнее задание.")
        Form.subject_added = 'Peoplelogy'
    elif user_text == "География":
        await message.reply("Вы выбрали предмет: География, введите домашнее задание.")
        Form.subject_added = 'Geography'
    else:
        await message.reply('Предмет не найден.')
        return
    await state.clear()

    await state.set_state(Form.hw)

@dp.message(Form.hw)
async def handle_response_admin(message: Message, state: FSMContext):
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d")
    user_text = message.text.strip()
    print(user_text)
    collhomework.update_one({'_id': 1}, {'$set': {Form.subject_added: f'{user_text}\nДата добавления: {formatted_time}'}})
    await message.reply(f'В базу данных к строке {Form.subject_added} добавлена строка {user_text}')

    await state.clear()

@dp.message()
async def where_a_homework(message: Message, state: FSMContext):
    result = collusers.find_one({'access_user_ids': {'id': message.from_user.id}})
    if result:
        user_text = message.text.strip()
        if user_text.lower() == ".алгебра":
            print(user_text.lower())
            subject_data = collhomework.find_one({'_id': 1})['Algebry']
            await message.answer(f"Информация по Алгебре: {subject_data}")
            return
        elif user_text.lower() == ".геометрия":
            subject_data = collhomework.find_one({'_id': 1})['Geometry']
            await message.answer(f"Информация по Геометрии: {subject_data}")
            return
        elif user_text.lower() == ".химия":
            subject_data = collhomework.find_one({'_id': 1})['Chemistry']
            await message.answer(f"Информация по Химии: {subject_data}")
            return
        elif user_text.lower() == ".физика":
            subject_data = collhomework.find_one({'_id': 1})['Physic']
            await message.answer(f"Информация по Физике: {subject_data}")
            return
        elif user_text.lower() == ".история":
            subject_data = collhomework.find_one({'_id': 1})['History']
            await message.answer(f"Информация по Истории: {subject_data}")
            return
        elif user_text.lower() == ".обж" or user_text.lower() == '.обзр':
            subject_data = collhomework.find_one({'_id': 1})['OBJ']
            await message.answer(f"Информация по ОБЖ: {subject_data}")
            return
        elif user_text.lower() == ".русский":
            subject_data = collhomework.find_one({'_id': 1})['Russian']
            await message.answer(f"Информация по Русскому: {subject_data}")
            return
        elif user_text.lower() == ".английский":
            subject_data = collhomework.find_one({'_id': 1})['English']
            await message.answer(f"Информация по Английскому: {subject_data}")
            return
        elif user_text.lower() == ".литература":
            subject_data = collhomework.find_one({'_id': 1})['Literature']
            await message.answer(f"Информация по Литературе: {subject_data}")
            return
        elif user_text.lower() == ".технология":
            subject_data = collhomework.find_one({'_id': 1})['Technology']
            await message.answer(f"Информация по Технологии: {subject_data}")
            return
        elif user_text.lower() == ".биология":
            subject_data = collhomework.find_one({'_id': 1})['Biology']
            await message.answer(f"Информация по Биологии: {subject_data}")
            return
        elif user_text.lower() == ".обществознание":
            subject_data = collhomework.find_one({'_id': 1})['Peoplelogy']
            await message.answer(f"Информация по Человековедению: {subject_data}")
            return
        elif user_text.lower() == ".география":
            subject_data = collhomework.find_one({'_id': 1})['Geography']
            await message.reply(f"Информация по Географии: {subject_data}")
            return
        if '.' in user_text:
            await message.answer("Предмет не найден. Попробуйте еще раз.")

@dp.message(Command('about'))
async def send_about(message: Message):
    result_time = Form.current_time.strftime('%d.%m.%Y')
    await message.reply(f'SchoolBot | Бот для получения информации о домашнем задании.\nРазработчик: @skefz\nАдмины: @skefz\nОнлайн с {result_time}')


async def main():
    await on_ready()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())

