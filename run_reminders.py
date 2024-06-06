import asyncio
import os

from aiogram import Bot
from dotenv import load_dotenv

from scheduler import check_and_send_reminders

load_dotenv()
bot = Bot(token=os.getenv('BOT_TOKEN'))


async def main():
    await check_and_send_reminders(bot)

if __name__ == "__main__":
    asyncio.run(main())
