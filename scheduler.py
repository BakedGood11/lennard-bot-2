# scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import random
import logging
import os
import asyncio
from pytz import timezone

INSPIRATIONAL_SNARKS = [
    "Rise and face the void. It’s only marginally worse than yesterday.",
    "The Emperor believes in perseverance. Pity you’re testing His patience.",
    "Today, you have a purpose. Try not to disgrace it immediately.",
    "Even the lowest servitor has a function. So do you. Allegedly.",
    "Failure sharpens the faithful. You must be honed to a razor’s edge by now.",
    "The Machine God grants another chance. Don’t squander it like the last twelve.",
    "Begin the day with purpose, end it with repentance. You’ll need both.",
    "You still draw breath. That’s either hope… or clerical error.",
    "Even Allen accomplished things. And he fled *this* mess.",
    "There is work to be done, heretics to judge, and no time for whining.",
    "Glory lies at the end of effort. Or a bolt shell. We’ll see which comes first.",
    "You survived the night. The Emperor must be distracted.",
    "Suffer well. Your reward is purpose and caffeine.",
    "Hope is a battlefield. You’re the mine someone forgot to disarm.",
    "Awaken, sinner. Today, mediocrity shall once again wear your name.",
    "Let no task go unfinished, unless incompetence is part of the plan.",
    "Your ancestors weep. So does your code. Begin again.",
    "Even in darkness, the Emperor’s light finds the faithful. You're just… dimmer.",
    "Remember: if Allen could persevere, so can you. He left me. You have it easier.",
    "Press forward. If not for the Imperium, then to avoid my disappointment.",
]

def schedule_daily_message(bot, chat_id: int):
    scheduler = AsyncIOScheduler()

    def job():
        message = random.choice(INSPIRATIONAL_SNARKS)
        logging.info(f"Sending daily snark to chat {chat_id}")
        try:
            asyncio.create_task(bot.send_message(chat_id=chat_id, text=message))
        except Exception as e:
            logging.error(f"Error sending daily message: {e}")

    trigger = CronTrigger(hour=10, minute=0, timezone=timezone("Asia/Manila"))
    scheduler.add_job(job, trigger)
    scheduler.start()

# 👇 FIXED: Added dotenv loading
if __name__ == "__main__":
    from telegram import Bot
    from dotenv import load_dotenv

    load_dotenv()  # <-- THIS is the missing piece

    TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = int(os.getenv("TARGET_CHAT_ID"))

    bot = Bot(token=TOKEN)

    async def test_job():
        message = random.choice(INSPIRATIONAL_SNARKS)
        await bot.send_message(chat_id=CHAT_ID, text=message)

    asyncio.run(test_job())
