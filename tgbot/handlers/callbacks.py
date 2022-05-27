import time
from aiogram import Dispatcher, types
from tgbot.services.repository import Repo


async def start_grade_saving(call: types.CallbackQuery, repo: Repo):
    grade_number = int(call.data.split(':')[-1])
    grade_letter_list = await repo.get_grade_letter_list(grade_number)
    grade_letter: str

    await call.answer()
    if len(grade_letter_list) == 1:
        grade_letter = grade_letter_list[0][0]

        await repo.add_user_grade(
            call.message.chat.id,
            grade_number, grade_letter)

        await call.message.edit_text(
            f'Данные сохранены. Ты учишься в {grade_number}{grade_letter} классе')

        time.sleep(0.7)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton(text='Сколько минут до звонка?'))
        await call.message.answer(
            'Спроси меня: "Сколько минут до звонка?"',
            reply_markup=keyboard)

    else:
        keyboard = types.InlineKeyboardMarkup()
        for l in grade_letter_list:
            keyboard.insert(types.InlineKeyboardButton(
                text=l[0], callback_data=f'grade_full:{grade_number}:{l[0]}'))

        await call.message.edit_text('Выбери букву', reply_markup=keyboard)


async def end_grade_saving(call: types.CallbackQuery, repo: Repo):
    grade_number = int(call.data.split(':')[-2])
    grade_letter = call.data.split(':')[-1]

    await repo.add_user_grade(call.message.chat.id, grade_number, grade_letter)

    await call.message.edit_text(
        f'Данные сохранены. Ты учишься в {grade_number}{grade_letter} классе')

    time.sleep(0.7)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='Сколько минут до звонка?'))
    await call.message.answer(
        'Спроси меня: "Сколько минут до звонка?"',
        reply_markup=keyboard)


def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(
        start_grade_saving, text_startswith='grade_number:')
    dp.register_callback_query_handler(
        end_grade_saving, text_startswith='grade_full:')
