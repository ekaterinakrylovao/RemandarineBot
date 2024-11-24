from aiogram import Router, Bot, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command

from attachments import messages as msg
from attachments import keyboards as kb
from filters.callback_data import NewCaseInterfaceCallback, RepeatCallback, NewCaseFinishWithFilesCallback
from filters.states import NewCaseStates
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale
from datetime import datetime
from database.db import db
from database.models import Cases, File

import os.path
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# from loguru import logger
import logging
import logging.config
from config import logger_conf

logging.config.dictConfig(logger_conf)

logger = logging.getLogger('my_python_logger')


router = Router()


@router.message(Command('new_mandarine'))
async def enter(message: Message, state: FSMContext, bot=Bot):
    await bot.send_message(chat_id=message.from_user.id, text="Введите название события")
    await state.set_state(NewCaseStates.set_case_name)
    logger.info(f"User {message.from_user.id} started creating new case", extra={'tags': {'user_id': message.from_user.id}})


@router.message(NewCaseStates.set_case_name, F.text)
async def choose_case_description(message: Message, state: FSMContext, bot=Bot):
    await state.update_data(name=message.text)
    attachments = []
    await state.update_data(attachments=attachments)
    await bot.send_message(chat_id=message.from_user.id, text="Хотите добавить описание?",
                           reply_markup=await kb.yes_no_kb())
    await state.set_state(NewCaseStates.add_case_description)


@router.callback_query(NewCaseStates.add_case_description,
                       NewCaseInterfaceCallback.filter(F.case_description_option == True))
async def set_case_description(query: CallbackQuery, state: FSMContext, bot=Bot):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    data = await state.get_data()
    name = data.get("name")
    await bot.send_message(chat_id=query.from_user.id, text=f"Напишите описание к событию _{name}_", parse_mode=ParseMode.MARKDOWN)
    await state.set_state(NewCaseStates.set_case_description)


@router.callback_query(NewCaseStates.add_case_description,
                       NewCaseInterfaceCallback.filter(F.case_description_option == False))
async def skip_case_description(query: CallbackQuery, state: FSMContext, bot=Bot):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    description = ''
    await state.update_data(description=description)
    await bot.send_message(chat_id=query.from_user.id, text="Продолжаем без описания\n"
                                                            "Выберите дату",
                           reply_markup=await SimpleCalendar(locale='ru_RU.utf8').start_calendar())
    await state.set_state(NewCaseStates.select_date)


@router.message(NewCaseStates.set_case_description)
async def set_case_date(message: Message, state: FSMContext, bot=Bot):
    await state.update_data(description=message.text)
    await bot.send_message(chat_id=message.from_user.id, text="Описанию быть!\n"
                                                              "Выберите дату",
                           reply_markup=await SimpleCalendar(locale='ru_RU.utf8').start_calendar())
    await state.set_state(NewCaseStates.select_date)


@router.callback_query(NewCaseStates.select_date, SimpleCalendarCallback.filter())
async def process_calendar(query: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(query, callback_data)
    if selected:
        await query.message.answer(
            "Вы выбрали дату: {}\nТеперь введите время в формате ЧЧ:ММ".format(
                date.strftime("%d.%m.%Y"))
        )
        await state.update_data(selected_date=date.strftime("%Y-%m-%d"))
        await state.set_state(NewCaseStates.select_time)


@router.message(NewCaseStates.select_time, F.text)
async def process_time(message: Message, state: FSMContext, bot: Bot):
    time_str = message.text
    data = await state.get_data()
    selected_date = data.get("selected_date")
    try:
        selected_time = datetime.strptime(time_str, "%H:%M").time()
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        full_datetime = datetime.combine(selected_date, selected_time)
        await state.update_data(selected_date=full_datetime.strftime("%Y-%m-%d %H:%M"))
        await bot.send_message(
            chat_id=message.from_user.id,
            text="Выберете частоту напоминания",
            reply_markup=await kb.get_repeat_keyboard()
        )
        await state.set_state(NewCaseStates.set_repeat)

    except ValueError:
        await message.answer("Формат времени неверный. Введите время в формате ЧЧ:ММ")


@router.callback_query(NewCaseStates.set_repeat, RepeatCallback.filter())
async def set_repeat(query: CallbackQuery, callback_data: RepeatCallback, state: FSMContext, bot=Bot):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    repeat_option = callback_data.repeat_option
    await state.update_data(repeat=repeat_option)
    await bot.send_message(chat_id=query.from_user.id, text=f"Выбранная Вами частота напоминания: {repeat_option}")
    await bot.send_message(chat_id=query.from_user.id, text=msg.NEW_CASE_FILES,
                           reply_markup=await kb.yes_no_kb())
    await state.set_state(NewCaseStates.add_attachments)


@router.callback_query(NewCaseStates.add_attachments, NewCaseInterfaceCallback.filter(F.case_files_option == False))
async def new_case(query: CallbackQuery, state: FSMContext, bot=Bot):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    user_id = query.from_user.id
    info = await state.get_data()
    selected_date = info["selected_date"]
    run_date = datetime.strptime(selected_date, "%Y-%m-%d %H:%M")
    print(info["selected_date"])
    case = db.create_object(
        Cases(user_id=user_id, name=info["name"], start_date=datetime.now(), description=info["description"],
              deadline_date=run_date, repeat=info["repeat"]))
    await bot.send_message(chat_id=query.from_user.id, text="Событие добавлено!", reply_markup=kb.main_kb)
    await state.clear()


@router.callback_query(NewCaseStates.add_attachments, NewCaseInterfaceCallback.filter(F.case_files_option == True))
async def case_files(query: CallbackQuery, state: FSMContext, bot=Bot):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    pick = await bot.send_message(chat_id=query.from_user.id,
                                  text="Прикрепите все необходимые файлы и нажмите, как всё будет прикреплено",
                                  reply_markup=await kb.set_new_case_with_files())
    await state.update_data(bot_message_id=pick.message_id)
    await state.set_state(NewCaseStates.set_files)


def get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def upload_file_to_drive(file_name, file_path, credentials):
    folder_id = os.getenv("FOLDER_ID")
    service = build('drive', 'v3', credentials=credentials)
    file_metadata = {'name': file_name,
                     'parents': [folder_id]}
    media = MediaFileUpload(file_path, mimetype='application/octet-stream')
    file = service.files().create(body=file_metadata, media_body=media, fields='id, parents').execute()

    file_id = file.get('id')
    return file_id


@router.message(NewCaseStates.set_files)
async def set_files(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    credentials = get_credentials()

    tmp_directory = 'tmp'
    if not os.path.exists(tmp_directory):
        os.makedirs(tmp_directory)

    file_path = None
    file_name = None

    if message.document:
        file_info = await message.bot.get_file(message.document.file_id)
        file_path = os.path.join(tmp_directory, file_info.file_unique_id)
        file_name = message.document.file_name

    elif message.photo:
        file_info = await message.bot.get_file(message.photo[-1].file_id)
        file_name = f"photo_{file_info.file_unique_id}.jpg"
        file_path = os.path.join(tmp_directory, file_name)

    if file_path and file_name:
        await message.bot.download_file(file_info.file_path, file_path)

        try:
            drive_file_url = upload_file_to_drive(file_name, file_path, credentials)
            attachments = data.get('attachments', [])
            attachment_info = f"{file_name}@@@{drive_file_url}"
            attachments.append(attachment_info)
            await state.update_data(attachments=attachments)

            # await message.answer(f"Файл {file_name} успешно загружен на Google Drive")

        except Exception as e:
            await message.answer(f"Произошла ошибка при загрузке файла {file_name} на Google Drive")
            print(e)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    else:
        await message.answer(
            "Прикрепите файл или завершите добавление, нажав на кнопку",
            reply_markup=await kb.set_new_case_with_files()
        )


@router.callback_query(NewCaseStates.set_files, NewCaseFinishWithFilesCallback.filter(F.finish_case == True))
async def finish_case_creation(query: CallbackQuery, state: FSMContext, bot=Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    info = await state.get_data()
    user_id = query.from_user.id
    selected_date = info["selected_date"]
    run_date = datetime.strptime(selected_date, "%Y-%m-%d %H:%M")
    case = db.create_object(
        Cases(user_id=user_id, name=info["name"], start_date=datetime.now(), description=info["description"],
              deadline_date=run_date, repeat=info["repeat"]))
    for attachment_info in info["attachments"]:
        file_name, file_url = attachment_info.split('@@@')
        db.create_object(File(file_name=file_name, file_url=file_url, case_id=case))
    await bot.send_message(chat_id=query.from_user.id, text="Событие добавлено!", reply_markup=kb.main_kb)
    await state.clear()
