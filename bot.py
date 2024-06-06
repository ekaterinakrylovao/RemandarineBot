import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import user, new_case, any, active_cases, finished_cases, today_cases
from scheduler import scheduler, router
from scheduler import check_and_send_reminders


load_dotenv()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()


dp.include_routers(user.router, new_case.router, active_cases.router, finished_cases.router, any.router, router)


async def main():
    # scheduler.add_job(check_and_send_reminders, 'interval', seconds=30, args=[bot])
    # scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        scheduler.shutdown()
