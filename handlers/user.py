from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.filters import CommandStart
from sqlalchemy import select

from attachments.keyboards import main_kb
from database.models import Users
from database.db import db

# from loguru import logger
import logging
import logging.config
from config import logger_conf

logging.config.dictConfig(logger_conf)

logger = logging.getLogger('my_python_logger')


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    existing_user = db.sql_query(query=select(Users).where(Users.id == user_id), is_single=True)

    if not existing_user:
        db.create_object(Users(id=user_id, username=username, first_name=first_name, last_name=last_name))
        await message.answer(text="Добро пожаловать в Remandarine Bot!",
                             reply_markup=main_kb)
        logger.info(f"New user created: {user_id} - {username}")
    else:
        await message.answer(text="С возвращением в Remandarine Bot!",
                             reply_markup=main_kb)
        logger.info(f"Existing user returned: {user_id} - {username}")


@router.message(Command('stop'))
async def stop(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Продолжаем работу в Remandarine Bot!",
                         reply_markup=main_kb)
    logger.info(f"User {message.from_user.id} stopped the bot")
