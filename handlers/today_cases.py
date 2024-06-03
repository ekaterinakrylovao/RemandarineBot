from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command
from attachments.keyboards import create_files_keyboard, create_cases_keyboard, create_case_management_keyboard
from filters.states import TodayCasesStates
from database.db import db
from sqlalchemy import select, update
from database.models import Cases, File
from filters.callback_data import FileCallback, CurrentCaseCallBack, ManageCaseCallback
from datetime import datetime


router = Router()


@router.message(Command(commands=['today_cases']))
async def get_current_cases(message: Message, state: FSMContext, bot: Bot):
    data = db.sql_query(select(Cases).where(Cases.user_id == str(message.from_user.id), Cases.is_finished == 'false',
                                            Cases.deadline_date == datetime.today().date()),
                        is_single=False)
    cases_keyboard = create_cases_keyboard(data)
    if not data:
        await bot.send_message(chat_id=message.from_user.id, text="У вас нет активных напоминаний на сегодня.")
        return
    await bot.send_message(chat_id=message.from_user.id, text='Ваши напоминания на сегодня', reply_markup=cases_keyboard)
    await state.set_state(TodayCasesStates.get_current_cases)


@router.callback_query(TodayCasesStates.get_current_cases, CurrentCaseCallBack.filter())
async def download_file(query: CallbackQuery, callback_data: FileCallback, bot: Bot, state: FSMContext):
    case_id = callback_data.case_id
    case = db.sql_query(select(Cases).where(Cases.id == case_id), is_single=True)
    reminders_msg = f"Дата: {case.deadline_date}\nНазвание: {case.name}\nОписание: {case.description}\nПовторение: {case.repeat}\n"
    management_keyboard = create_case_management_keyboard(case_id)
    await bot.send_message(chat_id=query.from_user.id, text=reminders_msg, reply_markup=management_keyboard)
    await state.set_state(TodayCasesStates.get_case_action)


@router.callback_query(TodayCasesStates.get_case_action, ManageCaseCallback.filter(F.action == "complete"))
async def complete_case(query: CallbackQuery, callback_data: ManageCaseCallback, bot: Bot):
    case_id = callback_data.case_id
    db.sql_query(query=update(Cases).where(Cases.id == case_id).values(is_finished=True), is_update=True)
    await bot.send_message(chat_id=query.from_user.id, text=f"Кейс {case_id} отмечен как выполненный.")


@router.callback_query(TodayCasesStates.get_case_action, ManageCaseCallback.filter(F.action == "files"))
async def show_files(query: CallbackQuery, callback_data: ManageCaseCallback, bot: Bot):
    case_id = callback_data.case_id
    files = db.sql_query(select(File).where(File.case_id == case_id), is_single=False)
    if files:
        files_keyboard = create_files_keyboard(files)
        await bot.send_message(chat_id=query.from_user.id, text="Файлы по кейсу:", reply_markup=files_keyboard)
    else:
        await bot.send_message(chat_id=query.from_user.id, text="У этого напоминания нет вложений :(")


@router.callback_query(TodayCasesStates.get_case_action, ManageCaseCallback.filter(F.action == "edit"))
async def edit_case(query: CallbackQuery, callback_data: ManageCaseCallback, bot: Bot):
    case_id = callback_data.case_id
    await bot.send_message(chat_id=query.from_user.id, text=f"Редактирование кейса {case_id}.")
