from aiogram import Dispatcher, types
from aiogram.dispatcher import filters

from psycopg2.errors import UniqueViolation

from tgbot.services.repository import Repo


async def user_start(m: types.Message, repo: Repo):
    chat_id = m.from_user.id
    first_name = m.from_user.first_name
    last_name = m.from_user.last_name
    user_name = m.from_user.username
    
    await m.answer(f'Привет, {first_name}')

    try:
        await repo.add_user(chat_id, first_name, last_name, user_name)
    except UniqueViolation:
        await repo.update_user(chat_id, first_name, last_name, user_name) 

    if await repo.has_user_grade(chat_id):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton(text='Сколько минут до звонка?'))
        await m.answer('Спроси меня: "Сколько минут до звонка?"', reply_markup=keyboard)
    else:
        await user_change_grade(m, repo)


async def user_change_grade(m: types.Message, repo: Repo):
    keyboard = types.InlineKeyboardMarkup()

    grade_numbers = await repo.get_grade_numbers_list()
    for g in grade_numbers:
        keyboard.insert(types.InlineKeyboardButton(text=str(g[0]), callback_data=f'grade_number:{g[0]}'))

    await m.answer('В каком классе ты учишься?', reply_markup=keyboard)

def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=['start'], state='*')
    dp.register_message_handler(user_change_grade, commands=['changegrade'], state='*')
