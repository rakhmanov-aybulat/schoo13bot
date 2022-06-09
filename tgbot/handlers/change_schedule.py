import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from ..models.role import UserRole
from ..services.repository import Repo
from ..services.excel import create_events_clarification_excel_template, parse_events_clarification_excel


class ChangeSchedule(StatesGroup):
    waiting_for_schedule_change_type = State()
    waiting_for_events_excel = State()
    waiting_for_events_clarification_excel = State()


async def send_events_clarification_excel_template(m: types.Message, repo: Repo):
    grade_list = await repo.get_grade_list()
    event_list = await repo.get_event_list()
    clarification_list = await repo.get_clarification_list()
    file_name = 'events.xlsx'
    create_events_clarification_excel_template(file_name, grade_list, event_list, clarification_list)

    file = types.InputFile(file_name, 'Расписание Шаблон.xlsx')
    await m.answer_document(file)


async def start_changing_schedule(m: types.Message):
    await ChangeSchedule.waiting_for_schedule_change_type.set()

    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = (
        types.InlineKeyboardButton(
            text='Изменть события', callback_data='schedule_change_type:events'),
        types.InlineKeyboardButton(
            text='Изменить уточнения событий', callback_data='schedule_change_type:events_clarification')
    )
    markup.add(*buttons)
    await m.answer('Что именно изменить?', reply_markup=markup)


async def schedule_change_type_chosen(call: types.CallbackQuery):
    schedule_change_type = call.data.split(':')[-1]
    if schedule_change_type == 'events':
        await ChangeSchedule.waiting_for_events_excel.set()
    elif schedule_change_type == 'events_clarification':
        await ChangeSchedule.waiting_for_events_clarification_excel.set()

    await call.message.edit_text('Отправь excel файл нового расписания.\n'
                                 '/schedule_template - чтобы посмотреть шаблон')

    await call.answer()


async def change_events_clarification(m: types.Message, repo: Repo, state: FSMContext):
    await state.finish()

    file_name = 'clarification.xlsx'

    bot = Bot.get_current()
    await bot.download_file_by_id(m.document.file_id, file_name)

    clarification_list = parse_events_clarification_excel(file_name)

    await repo.truncate_table('events_clarification')
    try:
        await repo.add_events_clarification(clarification_list)
    except Exception:
        await m.answer('Что-то пошло не так ')
    else:
        await m.answer('Уточнения событий изменены')

    if os.path.exists(file_name):
        os.remove(file_name)


def register_change_schedule(dp: Dispatcher):
    dp.register_message_handler(
        start_changing_schedule, commands=['change_schedule'],
        state='*', role=UserRole.ADMIN)
    dp.register_callback_query_handler(
        schedule_change_type_chosen, text_startswith='schedule_change_type',
        state=ChangeSchedule.waiting_for_schedule_change_type, role=UserRole.ADMIN)
    dp.register_message_handler(
        change_events_clarification, content_types=types.message.ContentType.DOCUMENT,
        state=ChangeSchedule.waiting_for_events_clarification_excel, role=UserRole.ADMIN)
    dp.register_message_handler(
        send_events_clarification_excel_template,
        commands=['schedule_template'], state='*', role=UserRole.ADMIN)
