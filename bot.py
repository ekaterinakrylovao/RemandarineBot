import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import user, new_case, any, active_cases, finished_cases, today_cases
from scheduler import scheduler, router
from scheduler import check_and_send_reminders

# import logging
# import logging.config
# from config import logger_conf


# logging.config.dictConfig(logger_conf)
#
# logger = logging.getLogger('my_python_logger')

import atexit
import json
import logging.config
import logging.handlers
import pathlib

logger = logging.getLogger(__name__)  # __name__ is a common choice


def setup_logging():
    config_file = pathlib.Path("config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)

    logging.config.dictConfig(config)
    # queue_handler = logging.getHandlerByName("queue_handler")
    # if queue_handler is not None:
    #     queue_handler.listener.start()
    #     atexit.register(queue_handler.listener.stop)


load_dotenv()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()


dp.include_routers(user.router, new_case.router, active_cases.router, finished_cases.router, any.router, router)


async def main():
    setup_logging()
    logger.info("Bot is starting")

    # scheduler.add_job(check_and_send_reminders, 'interval', seconds=30, args=[bot])
    # scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        # scheduler.shutdown()
        logger.info("Bot is shutting down")
