import logging
import time
from typing import Iterable

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from ..services.repository import Repo
from ..exceptions import CantGetGradeNumberList, CantGetGradeLetterList


logger = logging.getLogger(__name__)


class ChangeGrade(StatesGroup):
    waiting_for_grade_number = State()
    waiting_for_grade_letter = State()


def gen_grade_number_list_markup(grade_number_list: Iterable[int]) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for n in grade_number_list:
        markup.insert(types.InlineKeyboardButton(
            text=str(n), callback_data=f'grade_number:{n}'))
    return markup


def gen_grade_letter_list_markup(grade_letter_list: Iterable[str]) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for l in grade_letter_list:
        markup.insert(types.InlineKeyboardButton(
            text=str(l), callback_data=f'grade_letter:{l}'))
    return markup


def gen_ask_schedule_markup() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text='Сколько минут до звонка?'))
    return markup


async def start_grade(m: types.Message, repo: Repo) -> None:
    try:
        grade_number_list = await repo.get_grade_number_list()
    except CantGetGradeNumberList:
        logger.error('Can\'t get grade number list')

        await m.answer('Что-то пошло не так')
        return
    markup = gen_grade_number_list_markup(grade_number_list)

    await m.answer('В каком классе ты учишься?', reply_markup=markup)
    await ChangeGrade.waiting_for_grade_number.set()


async def grade_number_chosen(call: types.CallbackQuery, state: FSMContext, repo: Repo) -> None:
    grade_number = int(call.data.split(':')[-1])
    await state.update_data(grade_number=grade_number)

    try:
        grade_letter_list = await repo.get_grade_letter_list(grade_number)
    except CantGetGradeLetterList:
        logger.error('Can\'t get grade letter list')

        await state.finish()
        await call.message.edit_text('Что-то пошло не так')
        return

    if len(grade_letter_list) == 1:
        await state.finish()

        grade_letter = grade_letter_list[0]

        await end_grade(grade_number, grade_letter, call.message, repo)

    else:
        await ChangeGrade.next()

        markup = gen_grade_letter_list_markup(grade_letter_list)
        await call.message.edit_text('Выбери букву', reply_markup=markup)

    await call.answer()


async def grade_letter_chosen(call: types.CallbackQuery, state: FSMContext, repo: Repo) -> None:
    grade_letter: str = call.data.split(':')[-1]
    data = await state.get_data()
    grade_number: int = data.get('grade_number')

    await state.finish()

    await end_grade(grade_number, grade_letter, call.message, repo)

    await call.answer()


async def end_grade(grade_number: int, grade_letter: str, m: types.Message, repo: Repo) -> None:
    await repo.add_user_grade(m.chat.id, grade_number, grade_letter)

    await m.edit_text(
        f'Данные сохранены. Ты учишься в {grade_number}{grade_letter} классе')

    markup = gen_ask_schedule_markup()
    time.sleep(0.5)
    await m.answer('Спроси меня: "Сколько минут до звонка?"', reply_markup=markup)


def register_grades(dp: Dispatcher):
    dp.register_message_handler(start_grade, commands=['changegrade'], state='*')
    dp.register_callback_query_handler(
        grade_number_chosen, text_startswith='grade_number:', state=ChangeGrade.waiting_for_grade_number)
    dp.register_callback_query_handler(
        grade_letter_chosen, text_startswith='grade_letter:', state=ChangeGrade.waiting_for_grade_letter)
