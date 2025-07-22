from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("TARGET_CHAT_ID"))
bot = Bot(token=BOT_TOKEN)
import asyncio

async def test():
    await bot.send_message(chat_id=CHAT_ID, text="Manual test message")

asyncio.run(test())