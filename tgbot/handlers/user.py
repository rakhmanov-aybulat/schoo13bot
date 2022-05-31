from aiogram import Dispatcher, types
from psycopg2.errors import UniqueViolation

from ..handlers.grades import start_grade, gen_ask_schedule_markup
from ..services.repository import Repo


async def user_start(m: types.Message, repo: Repo):
    chat_id = m.from_user.id
    first_name = m.from_user.first_name
    last_name = m.from_user.last_name
    user_name = m.from_user.username

    await m.answer(f'Привет, {first_name}')

    try:
        await repo.add_user(chat_id, first_name, last_name, user_name)

        await start_grade(m, repo)

    except UniqueViolation:
        await repo.update_user(chat_id, first_name, last_name, user_name)

        markup = gen_ask_schedule_markup()
        await m.answer(
            'Спроси меня: "Сколько минут до звонка?"', reply_markup=markup)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=['start'], state='*')

