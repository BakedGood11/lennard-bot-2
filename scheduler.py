from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import random
import logging
import os
import asyncio
from pytz import timezone

# Middle-earth themed daily messages
DAILY_MESSAGES = [
    # Smeagol encouragements
    "Good morning, precious. Smeagol believes you’ll shine today, yessss.",
    "Rise, precious, and seize the day before it flees like a timid hobbit.",
    "Smeagol knows you can do it... don’t let us down, precious!",
    "Warm sun upon your face, precious. Make mistakes less harsh than shadows.",
    
    # Gollum’s darker quips
    "Awaken, fool! The shadows await your stumbles.",
    "The Precious demands action, not slumber. Move!",
    "Gollum’s patience wears thin—begone with your idle dreams!",
    "Even the worms will mock your laziness, precious.",
]

# Occasional Allen cameo
ALLEN_CAMEO = [
    "Allen once faced greater trials at dawn... what’s your excuse, precious?",
    "By Allen’s stubborn spirit, rise and do something worthwhile.",
    "Allen’s resolve outshines the morning sun—follow it, precious.",
]


def schedule_daily_message(bot, chat_id: int):
    """
    Schedule a daily check-in message in Gollum/Smeagol style at 10:00 Manila time.
    """
    scheduler = AsyncIOScheduler()

    def job():
        # Pick primary message
        message = random.choice(DAILY_MESSAGES)
        # 10% chance for Allen cameo
        if random.random() < 0.1:
            message += "\n" + random.choice(ALLEN_CAMEO)

        logging.info(f"Gollum: sending daily precious message to {chat_id}")
        try:
            asyncio.create_task(bot.send_message(chat_id=chat_id, text=message))
        except Exception as e:
            logging.error(f"Gollum error sending daily message: {e}")

    trigger = CronTrigger(hour=10, minute=0, timezone=timezone("Asia/Manila"))
    scheduler.add_job(job, trigger)
    scheduler.start()


# 👇 FIXED: Added dotenv loading for standalone testing
if __name__ == "__main__":
    from telegram import Bot
    from dotenv import load_dotenv

    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = int(os.getenv("TARGET_CHAT_ID", "0"))

    bot = Bot(token=TOKEN)

    async def test_job():
        message = random.choice(DAILY_MESSAGES)
        if random.random() < 0.1:
            message += "\n" + random.choice(ALLEN_CAMEO)
        await bot.send_message(chat_id=CHAT_ID, text=message)

    asyncio.run(test_job())
